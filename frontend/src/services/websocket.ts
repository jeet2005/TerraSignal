import { useMapStore, useAuthStore, useUIStore } from '../stores'
import { api } from './api'
import type { Event, CompoundEvent } from '../types'

type MessageHandler = (message: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private messageHandlers: Map<string, MessageHandler[]> = new Map()
  private isConnecting = false
  private shouldReconnect = true
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }
      
      if (this.isConnecting) {
        // Wait for existing connection attempt
        const checkConnection = setInterval(() => {
          if (this.ws?.readyState === WebSocket.OPEN) {
            clearInterval(checkConnection)
            resolve()
          } else if (!this.isConnecting) {
            clearInterval(checkConnection)
            reject(new Error('Connection failed'))
          }
        }, 100)
        return
      }
      
      this.isConnecting = true
      this.shouldReconnect = true
      
      try {
        const wsUrl = api.getWebSocketUrl()
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('[WS] Connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.send({ type: 'subscribe', channels: ['events', 'compound'] })
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (e) {
            console.error('[WS] Failed to parse message:', e)
          }
        }
        
        this.ws.onclose = (event) => {
          console.log('[WS] Disconnected:', event.code, event.reason)
          this.isConnecting = false
          this.ws = null
          
          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          }
        }
        
        this.ws.onerror = (error) => {
          console.error('[WS] Error:', error)
          this.isConnecting = false
          if (this.reconnectAttempts === 0) {
            reject(error)
          }
        }
      } catch (e) {
        this.isConnecting = false
        reject(e)
      }
    })
  }
  
  private scheduleReconnect() {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1)
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect().catch(() => {})
      }
    }, delay)
  }
  
  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
  }
  
  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('[WS] Cannot send, not connected')
    }
  }
  
  subscribe(channel: string, handler: MessageHandler) {
    if (!this.messageHandlers.has(channel)) {
      this.messageHandlers.set(channel, [])
    }
    this.messageHandlers.get(channel)!.push(handler)
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(channel)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index >= 0) handlers.splice(index, 1)
      }
    }
  }
  
  private handleMessage(message: any) {
    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message)
        } catch (e) {
          console.error(`[WS] Handler error for ${message.type}:`, e)
        }
      })
    }
    
    // Built-in handlers for core message types
    switch (message.type) {
      case 'event':
        useMapStore.getState().addEvents([message.data])
        useUIStore.getState().setLiveCount(
          useMapStore.getState().events.length + 1
        )
        break
        
      case 'events_batch':
        useMapStore.getState().addEvents(message.data)
        useUIStore.getState().setLiveCount(useMapStore.getState().events.length)
        break
        
      case 'compound_event':
        useMapStore.getState().addCompoundEvent(message.data)
        break
        
      case 'compound_events_batch':
        message.data.forEach((e: CompoundEvent) => 
          useMapStore.getState().addCompoundEvent(e)
        )
        break
        
      case 'compound_event_removed':
        useMapStore.getState().removeCompoundEvent(message.data.id)
        break
        
      case 'event_removed':
        useMapStore.getState().removeEvent(message.data.id)
        break
        
      case 'stats_update':
        useUIStore.getState().setLiveCount(message.data.total_events)
        break
        
      case 'pong':
        // Heartbeat response
        break
        
      default:
        // Unknown message type
        break
    }
  }
  
  // Subscribe to specific channels
  subscribeToEvents() {
    this.send({ type: 'subscribe', channels: ['events'] })
  }
  
  subscribeToCompoundEvents() {
    this.send({ type: 'subscribe', channels: ['compound'] })
  }
  
  unsubscribeFromEvents() {
    this.send({ type: 'unsubscribe', channels: ['events'] })
  }
  
  unsubscribeFromCompoundEvents() {
    this.send({ type: 'unsubscribe', channels: ['compound'] })
  }
  
  // Request initial data
  requestInitialData() {
    this.send({ type: 'get_initial_data' })
  }
  
  // Heartbeat
  startHeartbeat(interval = 30000) {
    setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
      }
    }, interval)
  }
}

export const ws = new WebSocketService()