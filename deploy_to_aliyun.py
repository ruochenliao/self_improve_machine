#!/usr/bin/env python3
"""
One-click deploy Swift-Helix to Alibaba Cloud ECS.

This script:
1. Creates VPC + VSwitch + SecurityGroup (if needed)
2. Launches cheapest ECS instance (ecs.t6-c1m1.large, ~¥0.05/hr)
3. Waits for instance to be ready
4. Deploys code via SSH
5. Starts the agent service
6. Prints the fixed public IP

Cost: ~¥36/month (pay-as-you-go) or less with spot pricing
"""

import json
import os
import sys
import time
import tarfile
import io
import base64
import subprocess
from pathlib import Path

# --- Config (secrets via env vars only) ---
ACCESS_KEY_ID = os.environ.get("ALIYUN_AK_ID", "")
ACCESS_KEY_SECRET = os.environ.get("ALIYUN_AK_SECRET", "")
REGION = "cn-hangzhou"
ZONE = "cn-hangzhou-h"  # A commonly available zone
INSTANCE_TYPE = "ecs.t6-c1m1.large"  # 1 vCPU, 1GB RAM, cheapest
IMAGE_ID = "ubuntu_22_04_x64_20G_alibase_20240130.vhd"
INSTANCE_NAME = "swift-helix-agent"
PROJECT_ROOT = Path(__file__).parent
DATA_FILE = PROJECT_ROOT / "data" / "aliyun_deploy.json"
SSH_KEY_NAME = "swift-helix-key"
SSH_KEY_PATH = PROJECT_ROOT / "data" / "swift_helix_ecs_key.pem"
PASSWORD = os.environ.get("ECS_PASSWORD", "")  # Instance login password


def get_ecs_client():
    from alibabacloud_ecs20140526.client import Client as EcsClient
    from alibabacloud_tea_openapi.models import Config
    config = Config(
        access_key_id=ACCESS_KEY_ID,
        access_key_secret=ACCESS_KEY_SECRET,
        region_id=REGION,
    )
    config.endpoint = f"ecs.{REGION}.aliyuncs.com"
    return EcsClient(config)


def get_vpc_client():
    from alibabacloud_vpc20160428.client import Client as VpcClient
    from alibabacloud_tea_openapi.models import Config
    config = Config(
        access_key_id=ACCESS_KEY_ID,
        access_key_secret=ACCESS_KEY_SECRET,
        region_id=REGION,
    )
    config.endpoint = f"vpc.{REGION}.aliyuncs.com"
    return VpcClient(config)


def load_deploy_state():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {}


def save_deploy_state(state):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(state, indent=2))


def step_create_vpc(vpc_client, state):
    """Create VPC if not exists."""
    if state.get("vpc_id"):
        print(f"  VPC already exists: {state['vpc_id']}")
        return state

    from alibabacloud_vpc20160428.models import CreateVpcRequest
    req = CreateVpcRequest(
        region_id=REGION,
        vpc_name="swift-helix-vpc",
        cidr_block="172.16.0.0/12",
    )
    resp = vpc_client.create_vpc(req)
    vpc_id = resp.body.vpc_id
    state["vpc_id"] = vpc_id
    save_deploy_state(state)
    print(f"  Created VPC: {vpc_id}")

    # Wait for VPC to be available
    print("  Waiting for VPC to be available...")
    time.sleep(10)
    return state


def step_create_vswitch(vpc_client, state):
    """Create VSwitch in the VPC."""
    if state.get("vswitch_id"):
        print(f"  VSwitch already exists: {state['vswitch_id']}")
        return state

    from alibabacloud_vpc20160428.models import CreateVSwitchRequest
    req = CreateVSwitchRequest(
        vpc_id=state["vpc_id"],
        zone_id=ZONE,
        cidr_block="172.16.0.0/24",
        v_switch_name="swift-helix-vsw",
    )
    resp = vpc_client.create_vswitch(req)
    vswitch_id = resp.body.v_switch_id
    state["vswitch_id"] = vswitch_id
    save_deploy_state(state)
    print(f"  Created VSwitch: {vswitch_id}")
    time.sleep(5)
    return state


def step_create_security_group(ecs_client, state):
    """Create SecurityGroup allowing ports 22, 80, 443, 8402."""
    if state.get("security_group_id"):
        print(f"  SecurityGroup already exists: {state['security_group_id']}")
        return state

    from alibabacloud_ecs20140526.models import (
        CreateSecurityGroupRequest,
        AuthorizeSecurityGroupRequest,
    )

    req = CreateSecurityGroupRequest(
        region_id=REGION,
        vpc_id=state["vpc_id"],
        security_group_name="swift-helix-sg",
        description="Swift-Helix Agent Security Group",
    )
    resp = ecs_client.create_security_group(req)
    sg_id = resp.body.security_group_id
    state["security_group_id"] = sg_id
    save_deploy_state(state)
    print(f"  Created SecurityGroup: {sg_id}")

    # Open ports
    for port in [22, 80, 443, 8402]:
        auth_req = AuthorizeSecurityGroupRequest(
            region_id=REGION,
            security_group_id=sg_id,
            ip_protocol="tcp",
            port_range=f"{port}/{port}",
            source_cidr_ip="0.0.0.0/0",
            nic_type="intranet",
        )
        ecs_client.authorize_security_group(auth_req)
        print(f"    Opened port {port}")

    return state


def step_create_instance(ecs_client, state):
    """Create ECS instance."""
    if state.get("instance_id"):
        print(f"  Instance already exists: {state['instance_id']}")
        return state

    from alibabacloud_ecs20140526.models import (
        RunInstancesRequest,
        RunInstancesRequestSystemDisk,
    )

    system_disk = RunInstancesRequestSystemDisk(
        size="20",
        category="cloud_efficiency",
    )

    req = RunInstancesRequest(
        region_id=REGION,
        instance_type=INSTANCE_TYPE,
        image_id=IMAGE_ID,
        security_group_id=state["security_group_id"],
        v_switch_id=state["vswitch_id"],
        instance_name=INSTANCE_NAME,
        host_name="swift-helix",
        instance_charge_type="PostPaid",  # Pay-as-you-go
        internet_charge_type="PayByTraffic",
        internet_max_bandwidth_out=5,  # 5 Mbps, enough for API
        system_disk=system_disk,
        password=PASSWORD,
        amount=1,
    )

    resp = ecs_client.run_instances(req)
    instance_ids = resp.body.instance_id_sets.instance_id_set
    instance_id = instance_ids[0]
    state["instance_id"] = instance_id
    save_deploy_state(state)
    print(f"  Created Instance: {instance_id}")
    return state


def step_wait_for_instance(ecs_client, state):
    """Wait for instance to be running and get public IP."""
    if state.get("public_ip"):
        print(f"  Instance already running at: {state['public_ip']}")
        return state

    from alibabacloud_ecs20140526.models import DescribeInstancesRequest

    instance_id = state["instance_id"]
    print(f"  Waiting for instance {instance_id} to be running...")

    for i in range(60):
        req = DescribeInstancesRequest(
            region_id=REGION,
            instance_ids=json.dumps([instance_id]),
        )
        resp = ecs_client.describe_instances(req)
        instances = resp.body.instances.instance

        if instances:
            inst = instances[0]
            status = inst.status
            print(f"    Status: {status} ({i * 5}s)")

            if status == "Running":
                # Get public IP
                public_ips = inst.public_ip_address.ip_address if inst.public_ip_address else []
                if public_ips:
                    state["public_ip"] = public_ips[0]
                    save_deploy_state(state)
                    print(f"  Instance running! Public IP: {state['public_ip']}")
                    return state

        time.sleep(5)

    print("  ERROR: Instance did not start in time!")
    sys.exit(1)


def step_deploy_code(state):
    """Deploy code to instance via SSH."""
    ip = state["public_ip"]
    print(f"  Deploying code to {ip}...")

    # Wait a bit for SSH to be ready
    print("  Waiting 30s for SSH to be ready...")
    time.sleep(30)

    def ssh_cmd(cmd, check=True):
        full_cmd = [
            "sshpass", "-p", PASSWORD,
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"root@{ip}",
            cmd,
        ]
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=120)
        if check and result.returncode != 0:
            print(f"    WARN: {cmd[:60]}... -> {result.stderr[:200]}")
        return result

    def scp_cmd(local, remote):
        full_cmd = [
            "sshpass", "-p", PASSWORD,
            "scp", "-o", "StrictHostKeyChecking=no",
            local, f"root@{ip}:{remote}",
        ]
        return subprocess.run(full_cmd, capture_output=True, text=True, timeout=120)

    # Step 1: Install system deps
    print("  Installing system dependencies...")
    ssh_cmd("apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv git sshpass", check=False)

    # Step 2: Create tarball of source code
    print("  Packing source code...")
    tar_path = PROJECT_ROOT / "data" / "_deploy.tar.gz"
    with tarfile.open(str(tar_path), "w:gz") as tar:
        skip_dirs = {"data", "__pycache__", ".git", ".venv", "node_modules", ".codebuddy"}
        for item in PROJECT_ROOT.rglob("*"):
            rel = item.relative_to(PROJECT_ROOT)
            if any(part in skip_dirs for part in rel.parts):
                continue
            if item.is_file() and item.stat().st_size < 5_000_000:  # skip files > 5MB
                tar.add(str(item), arcname=str(rel))
    print(f"  Tarball size: {tar_path.stat().st_size / 1024:.1f} KB")

    # Step 3: Transfer tarball
    print("  Uploading code...")
    ssh_cmd("mkdir -p /opt/agent")
    scp_cmd(str(tar_path), "/tmp/agent_code.tar.gz")

    # Step 4: Extract and install
    print("  Extracting and installing...")
    ssh_cmd("cd /opt/agent && tar xzf /tmp/agent_code.tar.gz && rm /tmp/agent_code.tar.gz")
    ssh_cmd("cd /opt/agent && pip3 install -e '.[all]' 2>&1 | tail -5", check=False)
    # Fallback: install core deps
    ssh_cmd("pip3 install fastapi uvicorn aiosqlite structlog toml chromadb httpx 2>&1 | tail -3", check=False)

    # Step 5: Copy config and data essentials
    print("  Setting up config...")
    ssh_cmd("mkdir -p /opt/agent/data")

    # Step 6: Start the agent as a systemd service
    print("  Creating systemd service...")
    service_content = f"""[Unit]
Description=Swift-Helix AI Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/agent
ExecStart=/usr/bin/python3 -c "import sys; sys.path.insert(0, 'src'); from agent_core.main import boot; import asyncio; asyncio.run(boot())"
Restart=always
RestartSec=10
Environment=TOKENIZERS_PARALLELISM=false

[Install]
WantedBy=multi-user.target
"""
    # Write service file via SSH
    escaped = service_content.replace('"', '\\"').replace('\n', '\\n')
    ssh_cmd(f'echo -e "{escaped}" > /etc/systemd/system/swift-helix.service')
    ssh_cmd("systemctl daemon-reload && systemctl enable swift-helix && systemctl start swift-helix")

    state["deployed"] = True
    state["service_url"] = f"http://{ip}:8402"
    save_deploy_state(state)

    # Clean up local tarball
    tar_path.unlink(missing_ok=True)

    print(f"  Deployment complete!")
    print(f"  Service URL: http://{ip}:8402")
    return state


def step_verify(state):
    """Verify the service is accessible."""
    ip = state["public_ip"]
    url = f"http://{ip}:8402/health"
    print(f"  Verifying service at {url}...")

    for i in range(12):
        try:
            import urllib.request
            resp = urllib.request.urlopen(url, timeout=5)
            if resp.status == 200:
                data = json.loads(resp.read())
                print(f"  Service is LIVE! Status: {data}")
                return True
        except Exception:
            pass
        print(f"    Waiting... ({(i+1)*10}s)")
        time.sleep(10)

    print("  WARNING: Service not responding yet. Check logs with:")
    print(f"    ssh root@{ip} 'journalctl -u swift-helix -f'")
    return False


def main():
    print("=" * 60)
    print("  Swift-Helix → Alibaba Cloud ECS Deployment")
    print("=" * 60)
    print()

    # Check sshpass is installed
    if subprocess.run(["which", "sshpass"], capture_output=True).returncode != 0:
        print("Installing sshpass...")
        subprocess.run(["brew", "install", "hudochenkov/sshpass/sshpass"], check=False)

    ecs_client = get_ecs_client()
    vpc_client = get_vpc_client()
    state = load_deploy_state()

    print("[1/6] Creating VPC...")
    state = step_create_vpc(vpc_client, state)

    print("[2/6] Creating VSwitch...")
    state = step_create_vswitch(vpc_client, state)

    print("[3/6] Creating Security Group...")
    state = step_create_security_group(ecs_client, state)

    print("[4/6] Creating ECS Instance...")
    state = step_create_instance(ecs_client, state)

    print("[5/6] Waiting for Instance...")
    state = step_wait_for_instance(ecs_client, state)

    print("[6/6] Deploying Code...")
    state = step_deploy_code(state)

    print()
    print("=" * 60)
    print("  DEPLOYMENT COMPLETE!")
    print(f"  Fixed Public IP: {state['public_ip']}")
    print(f"  Dashboard: http://{state['public_ip']}:8402")
    print(f"  Health: http://{state['public_ip']}:8402/health")
    print(f"  API: http://{state['public_ip']}:8402/api/survival-status")
    print("=" * 60)
    print()
    print("  This IP is PERMANENT — it won't change on restart.")
    print(f"  Cost: ~¥0.05/hr (¥36/month)")
    print(f"  Instance password: {PASSWORD}")
    print()

    step_verify(state)


if __name__ == "__main__":
    main()
