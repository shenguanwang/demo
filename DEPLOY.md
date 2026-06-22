# 云端部署

本项目包含Python后端，不能只部署为静态网站。

## Render

1. 将项目上传到GitHub私有仓库。
2. 登录 https://dashboard.render.com/
3. 选择 New > Blueprint。
4. 连接项目仓库，Render会读取根目录的 `render.yaml`。
5. 配置环境变量：
   - `GOOGLE_MAPS_API_KEY`：Google Places API密钥。
   - `PUBLIC_BASE_URL`：部署完成后的HTTPS地址。
6. 部署完成后访问 `/health`，应返回：

```json
{"ok": true, "service": "overseas-lead-workbench"}
```

## 数据说明

- 客户池和报价目前保存在访问者浏览器的 `localStorage` 中。
- `social-captures` 默认使用服务器本地文件。在无持久磁盘的免费实例重启后可能丢失。
- Chrome页面采集器默认发送到本机 `127.0.0.1:8815`，不会自动发送到公共Demo。
- `google_maps_api_key.txt` 已加入 `.gitignore`，不会上传。
