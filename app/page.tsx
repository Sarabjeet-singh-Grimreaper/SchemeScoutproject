import { redirect } from 'next/navigation'

export default function Home() {
  // Redirect to the static HTML frontend
  redirect('/index.html')
}
