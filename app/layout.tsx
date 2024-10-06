export const metadata = {
  title: '線画抽出アプリ',
  description: '線画抽出アプリ',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}
