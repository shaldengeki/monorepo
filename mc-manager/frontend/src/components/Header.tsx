import * as React from 'react'
import { ReactComponent as Logo } from './logo.svg'

const Header = () => {
  return (
    <div className="pb-3">
        <span className="w-24 h-24 inline-block text-center">
          <Logo className="inline max-h-24 max-w-24" alt="Logo" />
        </span>
        <span className="text-5xl text-gray-50">
            Minecraft Server Manager
        </span>
    </div>
  )
}

export default Header
