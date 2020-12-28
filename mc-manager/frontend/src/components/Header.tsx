import * as React from 'react'
import { ReactComponent as Logo } from './logo.svg'
import { Link } from 'react-router-dom'

const Header = () => {
  return (
    <div className="pb-3">
        <span className="w-24 h-24 inline-block text-center">
          <Logo className="inline max-h-24 max-w-24" />
        </span>
        <span className="text-5xl text-gray-50">
            <Link to="/">Minecraft Server Manager</Link>
        </span>
    </div>
  )
}

export default Header
