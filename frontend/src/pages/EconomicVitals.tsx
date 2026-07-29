import { Bitcoin, DollarSign, TrendingUp, Coffee, Globe } from 'lucide-react'
import { cn } from '../utils/cn'

interface CryptoData {
  name: string
  symbol: string
  price: number
  change: number
  color: string
}

interface FXData {
  pair: string
  rate: number
  change: number
}

interface MacroData {
  label: string
  value: string
  trend: 'up' | 'down' | 'flat'
  period: string
}

interface CommodityData {
  name: string
  price: number
  change: number
  unit: string
  color: string
}

const cryptoData: CryptoData[] = [
  { name: 'Bitcoin', symbol: 'BTC', price: 43250, change: 2.4, color: '#f7931a' },
  { name: 'Ethereum', symbol: 'ETH', price: 2340, change: 1.8, color: '#627eea' },
  { name: 'BNB', symbol: 'BNB', price: 315, change: -0.5, color: '#f3ba2f' },
  { name: 'Solana', symbol: 'SOL', price: 102, change: 4.2, color: '#9945ff' },
  { name: 'XRP', symbol: 'XRP', price: 0.52, change: 0.8, color: '#23292f' },
  { name: 'Cardano', symbol: 'ADA', price: 0.38, change: -1.2, color: '#0033ad' },
  { name: 'Avalanche', symbol: 'AVAX', price: 35.5, change: 3.1, color: '#e84142' },
  { name: 'Dogecoin', symbol: 'DOGE', price: 0.08, change: 2.7, color: '#c2a633' },
  { name: 'Polkadot', symbol: 'DOT', price: 7.2, change: -0.3, color: '#e6007a' },
  { name: 'Polygon', symbol: 'MATIC', price: 0.89, change: 1.5, color: '#8247e5' },
]

const fxData: FXData[] = [
  { pair: 'EUR/USD', rate: 1.0845, change: 0.23 },
  { pair: 'GBP/USD', rate: 1.2634, change: -0.11 },
  { pair: 'USD/JPY', rate: 149.82, change: 0.45 },
  { pair: 'USD/CHF', rate: 0.8756, change: -0.18 },
  { pair: 'AUD/USD', rate: 0.6543, change: 0.32 },
  { pair: 'USD/CAD', rate: 1.3567, change: -0.08 },
]

const macroData: MacroData[] = [
  { label: 'US Unemployment', value: '3.7%', trend: 'flat', period: 'Dec 2024' },
  { label: 'US CPI (YoY)', value: '3.1%', trend: 'down', period: 'Dec 2024' },
  { label: 'Fed Funds Rate', value: '5.25-5.50%', trend: 'flat', period: 'Current' },
  { label: '10Y Treasury', value: '4.02%', trend: 'up', period: 'Current' },
  { label: '30Y Mortgage', value: '6.87%', trend: 'down', period: 'Current' },
  { label: 'Consumer Confidence', value: '108.5', trend: 'up', period: 'Dec 2024' },
]

const commodityData: CommodityData[] = [
  { name: 'WTI Crude', price: 72.5, change: 1.8, unit: '/bbl', color: '#1e3a8a' },
  { name: 'Brent Crude', price: 77.2, change: 1.5, unit: '/bbl', color: '#1e3a8a' },
  { name: 'Natural Gas', price: 2.68, change: -3.2, unit: '/MMBtu', color: '#f59e0b' },
  { name: 'Gold', price: 2045, change: 0.8, unit: '/oz', color: '#fbbf24' },
  { name: 'Silver', price: 24.1, change: 2.1, unit: '/oz', color: '#9ca3af' },
  { name: 'Copper', price: 3.87, change: 2.4, unit: '/lb', color: '#b45309' },
  { name: 'Wheat', price: 582, change: -1.2, unit: '/bu', color: '#f59e0b' },
  { name: 'Corn', price: 445, change: 0.8, unit: '/bu', color: '#eab308' },
  { name: 'Coffee', price: 185, change: 4.5, unit: '/lb', color: '#78350f' },
]

function StatCard({ label, value, trend, icon: Icon, color }: { label: string; value: string; trend: 'up' | 'down' | 'flat'; icon: React.ComponentType<{ className?: string }>; color: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-dark-500">{label}</p>
          <p className="text-2xl font-bold text-dark-900 dark:text-dark-100 mt-1">{value}</p>
        </div>
        <div className="p-3 rounded-xl" style={{ backgroundColor: `${color}10` }}>
          <Icon className={cn('w-6 h-6', color)} style={{ color }} />
        </div>
      </div>
      <div className="mt-3">
        <span className={cn(
          'text-xs font-medium',
          trend === 'up' && 'text-green-600 dark:text-green-400',
          trend === 'down' && 'text-red-600 dark:text-red-400',
          trend === 'flat' && 'text-gray-500'
        )}>
          {trend === 'up' && '↑ '} {trend === 'down' && '↓ '} {trend === 'flat' && '→ '}
          {trend !== 'flat' && '24h'}
        </span>
      </div>
    </div>
  )
}

function CryptoRow({ coin }: { coin: CryptoData }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: coin.color }}>
        {coin.symbol.slice(0, 2)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-dark-900 dark:text-dark-100 truncate">{coin.name}</p>
        <p className="text-xs text-dark-500">{coin.symbol}</p>
      </div>
      <div className="text-right">
        <p className="font-medium text-dark-900 dark:text-dark-100">${coin.price.toLocaleString()}</p>
        <p className={cn(
          'text-xs font-medium',
          coin.change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
        )}>
          {coin.change >= 0 ? '+' : ''}{coin.change.toFixed(1)}%
        </p>
      </div>
    </div>
  )
}

function FXRow({ pair, rate, change }: { pair: string; rate: number; change: number }) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <span className="font-medium text-dark-900 dark:text-dark-100">{pair}</span>
      <div className="text-right">
        <p className="font-medium text-dark-900 dark:text-dark-100">{rate.toFixed(4)}</p>
        <p className={cn(
          'text-xs font-medium',
          change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
        )}>
          {change >= 0 ? '+' : ''}{change.toFixed(2)}%
        </p>
      </div>
    </div>
  )
}

function MacroRow({ label, value, trend, period }: MacroData) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <div>
        <p className="text-sm font-medium text-dark-900 dark:text-dark-100">{label}</p>
        <p className="text-xs text-dark-500">{period}</p>
      </div>
      <div className="text-right">
        <p className="font-bold text-dark-900 dark:text-dark-100">{value}</p>
        <p className={cn(
          'text-xs font-medium',
          trend === 'up' && 'text-green-600 dark:text-green-400',
          trend === 'down' && 'text-red-600 dark:text-red-400',
          trend === 'flat' && 'text-gray-500'
        )}>
          {trend === 'up' && '↑'} {trend === 'down' && '↓'} {trend === 'flat' && '→'}
        </p>
      </div>
    </div>
  )
}

function CommodityRow({ name, price, change, unit, color }: CommodityData) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="font-medium text-dark-900 dark:text-dark-100">{name}</span>
      </div>
      <div className="text-right">
        <p className="font-medium text-dark-900 dark:text-dark-100">${price.toLocaleString()}{unit}</p>
        <p className={cn(
          'text-xs font-medium',
          change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
        )}>
          {change >= 0 ? '+' : ''}{change.toFixed(1)}%
        </p>
      </div>
    </div>
  )
}

function Section({ title, icon: Icon, children }: { title: string; icon: React.ComponentType<{ className?: string }>; children: React.ReactNode }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4 p-4 border-b border-dark-200 dark:border-dark-800">
        <Icon className="w-5 h-5 text-primary-600" />
        <h3 className="font-semibold text-dark-900 dark:text-dark-100">{title}</h3>
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

export function EconomicVitals() {
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto space-y-6">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Economic Vitals
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          Global financial pulse — markets, currencies, macro indicators, commodities
        </p>
      </div>
      
      {/* Top Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          label="Bitcoin" 
          value="$43,250" 
          trend="up" 
          icon={Bitcoin} 
          color="#f7931a" 
        />
        <StatCard 
          label="Gold" 
          value="$2,045" 
          trend="up" 
          icon={TrendingUp} 
          color="#fbbf24" 
        />
        <StatCard 
          label="DXY Index" 
          value="102.4" 
          trend="down" 
          icon={DollarSign} 
          color="#3b82f6" 
        />
        <StatCard 
          label="VIX" 
          value="14.2" 
          trend="flat" 
          icon={TrendingUp} 
          color="#ef4444" 
        />
      </div>
      
      {/* Grid of panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Section title="Top Cryptocurrencies" icon={Bitcoin}>
          <div className="space-y-1">
            {cryptoData.map(coin => (
              <CryptoRow key={coin.symbol} coin={coin} />
            ))}
          </div>
        </Section>
        
        <Section title="Currency Movements" icon={DollarSign}>
          <div className="space-y-1">
            {fxData.map(fx => (
              <FXRow key={fx.pair} pair={fx.pair} rate={fx.rate} change={fx.change} />
            ))}
          </div>
        </Section>
        
        <Section title="Macro Indicators" icon={TrendingUp}>
          <div className="space-y-1">
            {macroData.map(m => (
              <MacroRow key={m.label} label={m.label} value={m.value} trend={m.trend} period={m.period} />
            ))}
          </div>
        </Section>
        
        <Section title="Commodities" icon={Coffee}>
          <div className="space-y-1">
            {commodityData.map(c => (
              <CommodityRow key={c.name} {...c} />
            ))}
          </div>
        </Section>
      </div>
      
      {/* Remittance Corridors */}
      <Section title="Remittance Corridors" icon={Globe}>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
            <span className="font-medium">USD → MXN</span>
            <span className="text-green-700 dark:text-green-400 font-bold">17.05</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20">
            <span className="font-medium">USD → INR</span>
            <span className="text-blue-700 dark:text-blue-400 font-bold">83.12</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-purple-50 dark:bg-purple-900/20">
            <span className="font-medium">USD → PHP</span>
            <span className="text-purple-700 dark:text-purple-400 font-bold">56.20</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-amber-50 dark:bg-amber-900/20">
            <span className="font-medium">AED → PKR</span>
            <span className="text-amber-700 dark:text-amber-400 font-bold">76.80</span>
          </div>
        </div>
      </Section>
    </div>
  )
}