import { useEffect } from 'react'

import { SITE } from '@/lib/site-config'

interface PageMetaProps {
  title: string
  description?: string
  path?: string
  type?: 'website' | 'article'
  noIndex?: boolean
}

function upsertMeta(name: string, content: string, property = false) {
  const attr = property ? 'property' : 'name'
  let element = document.querySelector(`meta[${attr}="${name}"]`)
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attr, name)
    document.head.appendChild(element)
  }
  element.setAttribute('content', content)
}

function upsertLink(rel: string, href: string) {
  let element = document.querySelector(`link[rel="${rel}"]`)
  if (!element) {
    element = document.createElement('link')
    element.setAttribute('rel', rel)
    document.head.appendChild(element)
  }
  element.setAttribute('href', href)
}

export function PageMeta({
  title,
  description = `${SITE.name} — slot game mathematics platform`,
  path = '',
  type = 'website',
  noIndex = false,
}: PageMetaProps) {
  const fullTitle = title === SITE.name ? title : `${title} · ${SITE.name}`
  const canonical = `${SITE.url}${path}`

  useEffect(() => {
    document.title = fullTitle
    upsertMeta('description', description)
    upsertMeta('robots', noIndex ? 'noindex, nofollow' : 'index, follow')
    upsertMeta('og:title', fullTitle, true)
    upsertMeta('og:description', description, true)
    upsertMeta('og:type', type, true)
    upsertMeta('og:url', canonical, true)
    upsertMeta('og:site_name', SITE.name, true)
    upsertMeta('twitter:card', 'summary_large_image')
    upsertMeta('twitter:title', fullTitle)
    upsertMeta('twitter:description', description)
    upsertLink('canonical', canonical)

    let jsonLd = document.getElementById('page-jsonld')
    if (!jsonLd) {
      jsonLd = document.createElement('script')
      jsonLd.id = 'page-jsonld'
      jsonLd.setAttribute('type', 'application/ld+json')
      document.head.appendChild(jsonLd)
    }
    jsonLd.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: fullTitle,
      description,
      url: canonical,
      isPartOf: {
        '@type': 'WebSite',
        name: SITE.name,
        url: SITE.url,
      },
    })
  }, [canonical, description, fullTitle, noIndex, type])

  return null
}
