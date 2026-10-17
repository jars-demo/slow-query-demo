import type { Metadata, Viewport } from 'next'
import { Fira_Code, Inter } from 'next/font/google'

import { Shell } from '@/components/Shell'

import './globals.css'

const sans = Inter({
  variable: '--font-face-sans',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
})
const mono = Fira_Code({
  variable: '--font-face-mono',
  subsets: ['latin'],
  weight: ['400', '500'],
})

export const metadata: Metadata = {
  title: { default: 'Make the slow query fast', template: '%s · Make the slow query fast' },
  description:
    'A hands-on database workshop: read query plans, choose the right index, fix N+1 queries, page without OFFSET and guard query plans in CI, with SQLite and plain Python.',
}

export const viewport: Viewport = { themeColor: '#ffffff' }

export default function RootLayout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <a
          href="#main"
          className="sr-only bg-ink px-4 py-2 text-canvas focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50"
        >
          Skip to content
        </a>
        <Shell>{children}</Shell>
      </body>
    </html>
  )
}
