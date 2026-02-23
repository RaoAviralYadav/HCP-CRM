import React from 'react'
import { Provider } from 'react-redux'
import { store } from './store'
import InteractionForm from './components/InteractionForm'
import AIAssistant from './components/AIAssistant'
import './index.css'

function App() {
  return (
    <Provider store={store}>
      <div className="app">
        <header className="app-header">
          <div className="header-left">
            <div className="logo">⚕</div>
            <div>
              <span className="app-name">LifeScience CRM</span>
              <span className="app-module">HCP Module</span>
            </div>
          </div>
          <div className="header-right">
            <span className="header-tag">AI-Powered</span>
          </div>
        </header>

        <main className="main-layout">
          <InteractionForm />
          <AIAssistant />
        </main>
      </div>
    </Provider>
  )
}

export default App