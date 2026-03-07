## Dev.to Integration Setup
1. Go to https://dev.to/settings/extensions
2. Click 'New Access Token' and copy the token
3. Update `/opt/agent/config/promotion.yaml` with:
```yaml
api_key: YOUR_TOKEN_HERE
```
4. Verify by running `/opt/agent/generated/test_devto_post.py