"use client";

interface FooterProps {
  isTurtle: boolean;
}

export default function Footer({ isTurtle }: FooterProps) {
  const NEXT_PUBLIC_GITHUB_URL = process.env.NEXT_PUBLIC_GITHUB_URL || '';
  const hrefURLs = [window.location.pathname, `${window.location.pathname}?turtle`];
  return (
    <footer>
      <div className="footer-links">
        <a href={NEXT_PUBLIC_GITHUB_URL} target="_blank" rel="noopener noreferrer">
          GitHub
        </a>
        {/* <span>
        ・
      </span> */}
        {/* {
        runMode === "server" ? (
          <a href="/">
            戻る
          </a>
        ) : (
          <a href="/another">
            サーバー版
          </a>
        )
      } */}
        <span>
          ・
        </span>
        {
          isTurtle ? (
            <a href={hrefURLs[0]}>
              🏠️
            </a>
          ) : (
            <a href={hrefURLs[1]}>
              🐢
            </a>
          )
        }
      </div>
      <div>
        Try this API by POST &#123; image: &#091;base64&#093; &#125; to <a href={isTurtle ? hrefURLs[1] : hrefURLs[0]}>/api/run</a>
      </div>
    </footer>
  )
}