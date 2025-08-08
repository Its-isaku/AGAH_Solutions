import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './style/index.css'

function TestApp() {
  return (
    <div>
      <h1>Test Page</h1>
      <p>If you can see this, React is working!</p>
    </div>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <TestApp />
  </StrictMode>
)
