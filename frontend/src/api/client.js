// Minimal fetch-based client (no axios dependency needed) exposing an axios-like `.post`/`.put`/`.get`.
function request(method) {
  return async (url, body, options = {}) => {
    const isFormData = body instanceof FormData
    const res = await fetch(url, {
      method,
      headers: isFormData ? undefined : { 'Content-Type': 'application/json', ...(options.headers || {}) },
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(`${method} ${url} failed: ${res.status} ${text}`)
    }
    const data = await res.json()
    return { data }
  }
}

export const api = {
  get: async (url) => {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`GET ${url} failed: ${res.status}`)
    return { data: await res.json() }
  },
  post: request('POST'),
  put: request('PUT'),
}
