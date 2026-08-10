# Static Blog

정적 HTML 블로그입니다. 별도 서버 프로그램이나 DB 없이 GitHub Pages, Cloudflare Pages, Netlify, 일반 웹호스팅에 업로드할 수 있습니다.

## 1. 먼저 설정
`site.config.json`에서 아래를 수정하세요.
- `siteName`: 블로그 이름
- `siteDescription`: 설명
- `siteUrl`: 실제 HTTPS 주소 (예: `https://blog.example.com`)
- `author`: 글 작성자
- `naverSiteVerification`: 네이버 서치어드바이저가 발급한 HTML 태그 인증값. 인증 파일 방식을 쓰면 비워도 됩니다.

수정 후:
```bash
python3 scripts/build.py
```

## 2. 새 글 게시
1. `posts/원하는-slug.html` 파일을 하나 만듭니다.
2. 기존 `posts/welcome.html`을 복사해서 제목, 본문, meta/canonical/구조화 데이터 URL과 날짜를 수정합니다.
3. `data/posts.json`에 글 정보를 추가합니다.
4. `python3 scripts/build.py` 실행.
5. 전체 폴더를 웹 루트에 배포합니다.

## 3. 글 목록 관리 파일
`data/posts.json`이 글 목록의 원본입니다.
`published: false`로 바꾸면 메인 목록, sitemap, RSS에서 제외됩니다.

## 4. 네이버 서치어드바이저
- 사이트를 HTTPS 주소 기준으로 등록하세요.
- 소유확인: HTML 파일 방식이면 네이버가 제공한 검증 파일을 이 프로젝트 루트에 그대로 넣고 배포합니다. HTML 태그 방식이면 `site.config.json`의 `naverSiteVerification`에 content 값을 입력하고 빌드합니다.
- 사이트맵 제출 주소: `/sitemap.xml`
- robots.txt는 `/robots.txt`에서 자동 제공됩니다.
- RSS 제출이 가능한 경우 `/rss.xml`도 활용할 수 있습니다.

## 구조
```
static-blog/
├── index.html
├── robots.txt
├── sitemap.xml
├── rss.xml
├── site.config.json
├── assets/style.css
├── data/posts.json
├── posts/welcome.html
└── scripts/build.py
```
