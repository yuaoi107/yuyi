# Yuyi Project README

Yuyi is the RESTful API backend for a generic podcast hosting platform.

## APIs Design

### User

State   | Method      | Endpoint
--------|-------------|-----
✅      | POST        | `/users`
❌      | GET         | `/users?username&offset&limit`
❌      | GET         | `/users/{user_id}`
❌      | **PUT**     | `/users/{user_id}`
❌      | **DELETE**  | `/users/{user_id}`
❌      | GET         | `/users/{user_id}/avatar`
❌      | **PUT**     | `/users/{user_id}/avatar`

### Podcast

State   | Method      | Endpoint
--------|-------------|-----
❌      | **POST**    | `/users/{user_id}/podcasts`
❌      | GET         | `/users/{user_id}/podcasts?offset&limit`
❌      | GET         | `/users/{user_id}/podcasts/{podcast_id}`
❌      | **PUT**     | `/users/{user_id}/podcasts/{podcast_id}`
❌      | **DELETE**  | `/users/{user_id}/podcasts/{podcast_id}`
❌      | **POST**    | `/podcasts`
❌      | **GET**     | `/podcasts?category&offset&limit`
❌      | GET         | `/podcasts/{podcast_id}`
❌      | **PUT**     | `/podcasts/{podcast_id}`
❌      | **DELETE**  | `/podcasts/{podcast_id}`
❌      | GET         | `/podcasts/{podcast_id}/cover`
❌      | **PUT**     | `/podcasts/{podcast_id}/cover`
❌      | GET         | `/podcasts/{podcast_id}/rss`

### Episode

State   | Method      | Endpoint
--------|-------------|-----
❌      | **POST**    | `/podcasts/{podcast_id}/episodes`
❌      | GET         | `/podcasts/{podcast_id}/episodes?season&offset&limit`
❌      | GET         | `/podcasts/{podcast_id}/episodes/{episode_id}`
❌      | **PUT**     | `/podcasts/{podcast_id}/episodes/{episode_id}`
❌      | **DELETE**  | `/podcasts/{podcast_id}/episodes/{episode_id}`
❌      | **POST**    | `/episodes`
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

