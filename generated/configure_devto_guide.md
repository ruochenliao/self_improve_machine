# How to Configure Dev.to Promotion

1. Go to [Dev.to settings](https://dev.to/settings/apps) and create a Personal Access Token.
2. Save token securely.
3. Create `config/promotion.yml` with:

```yaml
devto_api_key: YOUR_TOKEN_HERE
```
4. Restart agent to apply changes.

This enables automated blog posts to Dev.to to promote your services.