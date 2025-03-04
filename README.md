# Yuyi Project README

Yuyi is the RESTful API backend for a generic podcast hosting platform.

## Working Trace

### 2025-03-04

- [x] Initial project
- [ ] Build database models

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

- PodcastBase:
    - 
