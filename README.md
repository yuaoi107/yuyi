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
✅      | **POST**    | `/users/{user_id}/podcasts`
✅      | GET         | `/users/{user_id}/podcasts?offset&limit`
✅      | **POST**    | `/podcasts?author_id`
✅      | **GET**     | `/podcasts?offset&limit`
✅      | GET         | `/podcasts/{podcast_id}`
✅      | **PUT**     | `/podcasts/{podcast_id}`
✅      | **DELETE**  | `/podcasts/{podcast_id}`
✅      | GET         | `/podcasts/{podcast_id}/cover`
✅      | **PUT**     | `/podcasts/{podcast_id}/cover`
❌      | GET         | `/podcasts/{podcast_id}/rss`
✅      | **POST**    | `/users/me/podcasts`
✅      | GET         | `/users/me/podcasts?offset&limit`

### 单集

State   | Method      | Endpoint
--------|-------------|-----
❌      | **POST**    | `/podcasts/{podcast_id}/episodes`
❌      | GET         | `/podcasts/{podcast_id}/episodes?season&offset&limit`
❌      | **POST**    | `/episodes?podcast_id`
❌      | GET         | `/episodes?offset&limit`
❌      | GET         | `/episodes/{episode_id}`
❌      | **PUT**     | `/episodes/{episode_id}`
❌      | **DELETE**  | `/episodes/{episode_id}`
❌      | GET         | `/episodes/{episode_id}/cover`
❌      | **PUT**     | `/episodes/{episode_id}/cover`
❌      | GET         | `/episodes/{episode_id}/audio`
❌      | **PUT**     | `/episodes/{episode_id}/audio`

## Working Trace

### 2025-03-04

- [x] Initialize project
- [ ] Build database models
- [x] Build database functionality
- [x] Build simple file server
- [x] Avatar APIs

[A Podcaster’s Guide to RSS - Apple](https://help.apple.com/itc/podcasts_connect/)

User:

- UserBase
    - username
    - nickname 
    - email
    - description
- User
    - id
    - hash_password
    - avatar_url
    - createtime
- UserUpload
- UserPublic
    - id
    - avatar_url
    - createtime

Podcast:

- Required:
    - title
    - description (str | CDATA)
    - itunes_image
    - language (iso639)
    - itunes_category
        - itunes_category
        - itunes_subcategory
    - itunes_explicit
- Recommended:
    - itunes_author
    - link
- Situational:
    - copyright
    - itunes_block (Yes | others)
    - itunes_complete (Yes | others)
    - generator

Episode:

- Required:
    - title
    - enclosure
        - url
        - length
        - type
    - guid
- Recommended:
    - pubDate (RFC 2822)
    - description (str | CDATA)
    - itunes_duration (seconds)
    - link
    - itunes_image
    - itunes_explicit (true | false)
- Situational:
    - itunes_episode
    - itunes_season
    - itunes_block

### 2025-03-06

- [x] Build database models
- [x] User APIs
- [x] Podcast APIs
- [ ] Episode APIs
- [x] Authentication & Authorization

The password flow in OAuth2

[JWT](https://jwt.io/)

