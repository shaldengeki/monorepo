import * as React from 'react'
import logo from './logo.svg'

const Header = () => {
  return (
    <div className="pb-3">
        <span className="w-24 h-24 inline-block text-center">
            <img className="inline max-h-24 max-w-24" src={logo} alt="Logo" />
        </span>
        <span className="text-5xl">
            Minecraft Server Manager
        </span>
    </div>
  )
}

export default Header
