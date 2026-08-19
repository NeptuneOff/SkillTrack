import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'

test('renders SkillTrack title', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: /suivi structuré/i })).toBeInTheDocument()
})
