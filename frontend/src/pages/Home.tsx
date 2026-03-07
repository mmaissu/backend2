import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth'
import Landing from './Landing'

export default function Home() {
  const { token } = useAuth()
  if (token) return <Navigate to="/articles" replace />
  return <Landing />
}
