import { Activity, Github, Zap, Wifi, ArrowUpRight, Terminal, Code, MessageSquare, TrendingUp, Satellite, Triangle, Circle, CheckCircle, AlertTriangle } from 'lucide-react'
import { cn } from '../utils/cn'

const wikiEdits = [
  { title: '2024 Noto Peninsula earthquake', user: 'EarthquakeBot', time: '2 min ago', comment: 'Updated casualty figures', diffUrl: '#' },
  { title: '2024 Chile wildfires', user: 'FireMonitor', time: '5 min ago', comment: 'Added evacuation zones', diffUrl: '#' },
  { title: 'Gaza Strip', user: 'PeaceWatcher', time: '8 min ago', comment: 'Updated humanitarian situation', diffUrl: '#' },
  { title: 'Typhoon Saola', user: 'StormChaser99', time: '12 min ago', comment: 'Added landfall data', diffUrl: '#' },
  { title: 'Ukraine conflict', user: 'HistoryEditor', time: '18 min ago', comment: 'Frontline updates', diffUrl: '#' },
  { title: 'Bitcoin', user: 'CryptoBot', time: '22 min ago', comment: 'Price update', diffUrl: '#' },
  { title: 'AI safety', user: 'TechEthicist', time: '25 min ago', comment: 'Added new research', diffUrl: '#' },
  { title: 'Climate change', user: 'EcoEditor', time: '30 min ago', comment: 'COP28 outcomes', diffUrl: '#' },
]

const githubEvents = [
  { repo: 'vercel/next.js', type: 'PushEvent', user: 'timer', time: '1 min ago', details: '3 commits to main' },
  { repo: 'facebook/react', type: 'IssuesEvent', user: 'acdlite', time: '3 min ago', details: 'Opened issue #28491' },
  { repo: 'microsoft/vscode', type: 'PullRequestEvent', user: 'bpasero', time: '5 min ago', details: 'PR #192341 merged' },
  { repo: 'kubernetes/kubernetes', type: 'PushEvent', user: 'k8s-ci-robot', time: '8 min ago', details: '2 commits to release-1.29' },
  { repo: 'rust-lang/rust', type: 'ReleaseEvent', user: 'rustbot', time: '12 min ago', details: 'Published 1.76.0' },
  { repo: 'golang/go', type: 'IssuesEvent', user: 'gopherbot', time: '15 min ago', details: 'Closed issue #64892' },
  { repo: 'tensorflow/tensorflow', type: 'PushEvent', user: 'tf-bot', time: '20 min ago', details: '4 commits to master' },
  { repo: 'apache/spark', type: 'PullRequestEvent', user: 'spark-qa', time: '25 min ago', details: 'PR #42156 opened' },
]

const hnStories = [
  { title: 'Show HN: I built a real-time earthquake tracker', score: 342, comments: 89, time: '2 hours ago', url: '#' },
  { title: 'How Starlink handles 1M+ concurrent connections', score: 567, comments: 134, time: '3 hours ago', url: '#' },
  { title: 'The architecture of GitHub Codespaces', score: 423, comments: 67, time: '4 hours ago', url: '#' },
  { title: 'Real-time collaboration with CRDTs', score: 289, comments: 45, time: '5 hours ago', url: '#' },
  { title: 'Building a global CDN from scratch', score: 156, comments: 23, time: '6 hours ago', url: '#' },
  { title: 'PostgreSQL 17: What\'s new for developers', score: 234, comments: 34, time: '7 hours ago', url: '#' },
  { title: 'The rise of WebAssembly in production', score: 178, comments: 28, time: '8 hours ago', url: '#' },
  { title: 'Optimizing WebSocket connections at scale', score: 112, comments: 19, time: '9 hours ago', url: '#' },
]

const cloudflareData = [
  { region: 'North America', status: 'healthy', traffic: '2.4 Tbps', incidents: 0 },
  { region: 'Europe', status: 'healthy', traffic: '1.8 Tbps', incidents: 0 },
  { region: 'Asia Pacific', status: 'degraded', traffic: '1.2 Tbps', incidents: 2 },
  { region: 'South America', status: 'healthy', traffic: '340 Gbps', incidents: 0 },
  { region: 'Africa', status: 'healthy', traffic: '180 Gbps', incidents: 0 },
  { region: 'Middle East', status: 'healthy', traffic: '220 Gbps', incidents: 1 },
]

const solarFlares = [
  { class: 'X1.2', time: '14:23 UTC', region: 'AR3664', peak: '14:35 UTC' },
  { class: 'M7.4', time: '12:15 UTC', region: 'AR3664', peak: '12:28 UTC' },
  { class: 'M5.1', time: '10:42 UTC', region: 'AR3664', peak: '10:55 UTC' },
  { class: 'M3.8', time: '08:21 UTC', region: 'AR3658', peak: '08:34 UTC' },
  { class: 'C9.4', time: '06:15 UTC', region: 'AR3658', peak: '06:22 UTC' },
]

const geoStorms = [
  { level: 'G3', time: '15:00 UTC', duration: '6h', kp: 7 },
  { level: 'G2', time: '09:00 UTC', duration: '12h', kp: 6 },
  { level: 'G1', time: '03:00 UTC', duration: '9h', kp: 5 },
]

const cmeEvents = [
  { time: '14:35 UTC', speed: '1200 km/s', angle: '45°', arrival: 'Apr 25 18:00 UTC' },
  { time: '12:28 UTC', speed: '850 km/s', angle: '30°', arrival: 'Apr 26 06:00 UTC' },
  { time: '10:55 UTC', speed: '600 km/s', angle: '15°', arrival: 'Apr 26 18:00 UTC' },
]

function StatCard({ label, value, trend, color }: { label: string; value: string; trend: 'up' | 'down' | 'flat'; color: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-dark-500">{label}</p>
          <p className="text-2xl font-bold text-dark-900 dark:text-dark-100">{value}</p>
        </div>
        <div className={cn(
          'p-2 rounded-lg',
          trend === 'up' && 'bg-green-100 dark:bg-green-900/30',
          trend === 'down' && 'bg-red-100 dark:bg-red-900/30',
          trend === 'flat' && 'bg-gray-100 dark:bg-gray-900/30'
        )} style={{ backgroundColor: `${color}20` }}>
          <div className={cn(
            'w-2 h-2 rounded-full',
            trend === 'up' && 'bg-green-500',
            trend === 'down' && 'bg-red-500',
            trend === 'flat' && 'bg-gray-500'
          )} />
        </div>
      </div>
    </div>
  )
}

function Section({ title, icon: Icon, children, status }: { title: string; icon: React.ComponentType<{ className?: string }>; children: React.ReactNode; status?: string }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4 p-4 border-b border-dark-200 dark:border-dark-800">
        <div className="flex items-center gap-2">
          <Icon className="w-5 h-5 text-primary-600" />
          <h3 className="font-semibold text-dark-900 dark:text-dark-100">{title}</h3>
        </div>
        {status && (
          <span className={cn(
            'px-2 py-0.5 text-xs rounded-full',
            status === 'healthy' && 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
            status === 'elevated' && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
            status === 'storm' && 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
            status === 'degraded' && 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
          )}>
            {status}
          </span>
        )}
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

function FlareRow({ flare }: { flare: typeof solarFlares[0] }) {
  const isX = flare.class.startsWith('X')
  const isM = flare.class.startsWith('M')
  return (
    <div className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <div className="flex items-center gap-2">
        <span className={cn(
          'px-2 py-0.5 text-xs font-bold rounded',
          isX && 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
          isM && 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
        )}>
          {flare.class}
        </span>
        <span className="text-sm font-medium text-dark-900 dark:text-dark-100">{flare.region}</span>
      </div>
      <div className="text-right text-xs text-dark-500">
        <div>{flare.time}</div>
        <div>Peak: {flare.peak}</div>
      </div>
    </div>
  )
}

function StormRow({ storm }: { storm: typeof geoStorms[0] }) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <div className="flex items-center gap-2">
        <span className="px-2 py-0.5 text-xs font-bold rounded bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300">
          {storm.level}
        </span>
        <span className="text-sm text-dark-900 dark:text-dark-100">Kp {storm.kp}</span>
      </div>
      <div className="text-right text-xs text-dark-500">
        <div>{storm.time}</div>
        <div>Duration: {storm.duration}</div>
      </div>
    </div>
  )
}

function CMERow({ cme }: { cme: typeof cmeEvents[0] }) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <div>
        <div className="text-sm font-medium text-dark-900 dark:text-dark-100">{cme.speed}</div>
        <div className="text-xs text-dark-500">Angle: {cme.angle}</div>
      </div>
      <div className="text-right text-xs text-dark-500">
        <div>{cme.time}</div>
        <div>Arrival: {cme.arrival}</div>
      </div>
    </div>
  )
}

function ISSInfo() {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-4 gap-3 text-center">
        <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
          <p className="text-dark-500">Orbit Period</p>
          <p className="font-mono font-bold text-dark-900 dark:text-dark-100">92.9 min</p>
        </div>
        <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
          <p className="text-dark-500">Inclination</p>
          <p className="font-mono font-bold text-dark-900 dark:text-dark-100">51.6°</p>
        </div>
        <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
          <p className="text-dark-500">Altitude</p>
          <p className="font-mono font-bold text-dark-900 dark:text-dark-100">408 km</p>
        </div>
        <div className="p-3 bg-dark-50 dark:bg-dark-900 rounded-lg">
          <p className="text-dark-500">Velocity</p>
          <p className="font-mono font-bold text-dark-900 dark:text-dark-100">7.66 km/s</p>
        </div>
      </div>
      
      <div className="p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
        <p className="text-sm text-primary-800 dark:text-primary-300">
          Next visible pass: <span className="font-mono font-bold">19:42 UTC</span> (Duration: 6 min)
        </p>
      </div>
    </div>
  )
}

function UpcomingPasses() {
  return (
    <div className="space-y-2">
      {[
        { time: '19:42 UTC', duration: '6 min', maxAlt: '67°', direction: 'SW → NE' },
        { time: '21:18 UTC', duration: '4 min', maxAlt: '42°', direction: 'W → E' },
        { time: '22:55 UTC', duration: '2 min', maxAlt: '18°', direction: 'NW → N' },
      ].map((pass, i) => (
        <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary-500" />
            <span className="font-mono text-sm text-dark-900 dark:text-dark-100">{pass.time}</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-dark-500">
            <span>{pass.duration}</span>
            <span>Max: {pass.maxAlt}</span>
            <span>{pass.direction}</span>
          </div>
        </div>
      ))}
    </div>
  )
}

export function SpaceWindow() {
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto space-y-6">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Space Window
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          Solar activity, geomagnetic storms, and orbital traffic
        </p>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Solar Flux (SFU)" value="145" trend="up" color="#f59e0b" />
        <StatCard label="Kp Index" value="4" trend="flat" color="#3b82f6" />
        <StatCard label="Solar Wind" value="420 km/s" trend="flat" color="#10b981" />
        <StatCard label="X-ray Flux" value="B2.1" trend="down" color="#8b5cf6" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Section title="Recent Solar Flares" icon={Zap} status="elevated">
          <div className="space-y-1">
            {solarFlares.map((flare, i) => (
              <FlareRow key={i} flare={flare} />
            ))}
          </div>
        </Section>
        
        <Section title="Geomagnetic Storms" icon={TrendingUp} status="storm">
          <div className="space-y-1">
            {geoStorms.map((storm, i) => (
              <StormRow key={i} storm={storm} />
            ))}
          </div>
        </Section>
        
        <Section title="Coronal Mass Ejections" icon={Circle} status="elevated">
          <div className="space-y-1">
            {cmeEvents.map((cme, i) => (
              <CMERow key={i} cme={cme} />
            ))}
          </div>
        </Section>
        
        <Section title="ISS Current Position" icon={Satellite} status="healthy">
          <ISSInfo />
        </Section>
        
        <Section title="Upcoming ISS Passes" icon={Triangle} status="healthy">
          <UpcomingPasses />
        </Section>
        
        <Section title="Space Weather Alerts" icon={AlertTriangle} status="degraded">
          <div className="space-y-2">
            <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                <span className="font-medium text-yellow-800 dark:text-yellow-300">G3 Watch Active</span>
              </div>
              <p className="text-sm text-yellow-700 dark:text-yellow-400">
                Strong geomagnetic storm possible. HF radio blackouts likely at high latitudes.
              </p>
            </div>
            <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="font-medium text-green-800 dark:text-green-300">R1-R2 Radio Blackouts</span>
              </div>
              <p className="text-sm text-green-700 dark:text-green-400">
                Minor to moderate radio blackouts ongoing on sunlit side of Earth.
              </p>
            </div>
          </div>
        </Section>
      </div>
    </div>
  )
}