/// <reference types="astro/client" />

declare global {
  interface Window {
    Gitalk: new (config: Record<string, unknown>) => {
      render: (containerId: string) => void
    }
  }

  const Gitalk: Window['Gitalk']
}

export {}
