import { useEffect } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { api } from './api'

export function AuthTokenProvider({ children }: { children: React.ReactNode }) {
  const { getAccessTokenSilently } = useAuth0()

  useEffect(() => {
    const interceptor = api.interceptors.request.use(async (config) => {
      try {
        const token = await getAccessTokenSilently()
        config.headers.Authorization = `Bearer ${token}`
      } catch {
        // Not authenticated — let the request go through unauthenticated;
        // the API will return 401 and the router will redirect to login.
      }
      return config
    })
    return () => api.interceptors.request.eject(interceptor)
  }, [getAccessTokenSilently])

  return <>{children}</>
}
