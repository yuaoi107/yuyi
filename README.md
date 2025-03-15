# 雨呓

雨呓（Yuyi）是一个泛用型播客托管平台的 RESTful API 后端。

## API 设计

### 用户

State   | Method      | Endpoint
--------|-------------|-----
✅      | POST        | `/users`
✅      | GET         | `/users?offset&limit`
✅      | **GET**     | `/users/me`
✅      | **PUT**     | `/users/me`
✅      | **DELETE**  | `/users/me`
✅      | **PUT**     | `/users/me/avatar`
✅      | **GET**     | `/users/me/avatar`
✅      | GET         | `/users/{user_id}`
✅      | **PUT**     | `/users/{user_id}`
✅      | **DELETE**  | `/users/{user_id}`
✅      | GET         | `/users/{user_id}/avatar`
✅      | **PUT**     | `/users/{user_id}/avatar`

### 播客

State   | Method      | Endpoint
--------|-------------|-----
✅      | **POST**    | `/users/me/podcasts`
✅      | GET         | `/users/me/podcasts?offset&limit`
✅      | **POST**    | `/users/{user_id}/podcasts`
✅      | GET         | `/users/{user_id}/podcasts?offset&limit`
✅      | **POST**    | `/podcasts?author_id`
✅      | **GET**     | `/podcasts?offset&limit`
✅      | GET         | `/podcasts/{podcast_id}`
✅      | **PUT**     | `/podcasts/{podcast_id}`
✅      | **DELETE**  | `/podcasts/{podcast_id}`
✅      | GET         | `/podcasts/{podcast_id}/cover`
✅      | **PUT**     | `/podcasts/{podcast_id}/cover`
✅      | GET         | `/podcasts/{podcast_id}/rss`

### 单集

State   | Method      | Endpoint
--------|-------------|-----
✅      | **POST**    | `/episodes?podcast_id`
✅      | GET         | `/episodes?keyword&offset&limit`
✅      | GET         | `/episodes/{episode_id}`
✅      | **PUT**     | `/episodes/{episode_id}`
✅      | **DELETE**  | `/episodes/{episode_id}`
✅      | GET         | `/episodes/{episode_id}/cover`
✅      | **PUT**     | `/episodes/{episode_id}/cover`
✅      | GET         | `/episodes/{episode_id}/audio`
✅      | **PUT**     | `/episodes/{episode_id}/audio`
✅      | **POST**    | `/podcasts/{podcast_id}/episodes`
✅      | GET         | `/podcasts/{podcast_id}/episodes?offset&limit`

