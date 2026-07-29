import { Activity, Github, Zap, Wifi, Terminal, Code, MessageSquare, TrendingUp, ArrowUpRight } from 'lucide-react'
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

function WikiEditRow({ edit }: { edit: typeof wikiEdits[0] }) {
  return (
    <a href={edit.diffUrl} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors group">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-dark-900 dark:text-dark-100 truncate">{edit.title}</p>
        <p className="text-xs text-dark-500">{edit.user} • {edit.time} • {edit.comment}</p>
      </div>
      <ArrowUpRight className="w-4 h-4 text-dark-400 group-hover:text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity" />
    </a>
  )
}

function GHEventRow({ event }: { event: typeof githubEvents[0] }) {
  return (
    <div className="p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-primary-600 dark:text-primary-400">{event.repo}</span>
        <span className="text-xs text-dark-500">{event.time}</span>
      </div>
      <p className="text-sm text-dark-900 dark:text-dark-100 mt-1">{event.details}</p>
      <p className="text-xs text-dark-500">{event.type.replace('Event', '')} by {event.user}</p>
    </div>
  )
}

function HNStoryRow({ story }: { story: typeof hnStories[0] }) {
  return (
    <a href={story.url} target="_blank" rel="noopener noreferrer" className="flex items-start gap-3 p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors group">
      <div className="flex flex-col items-center text-xs text-dark-400 min-w-[3.5rem]">
        <span className="font-bold text-dark-900 dark:text-dark-100">{story.score}</span>
        <span>pts</span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-dark-900 dark:text-dark-100 truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{story.title}</span>
        <p className="text-xs text-dark-500 mt-1">{story.comments} comments • {story.time}</p>
      </div>
    </a>
  )
}

function CFRegionRow({ region }: { region: { region: string; status: string; traffic: string; incidents: number } }) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg hover:bg-dark-50 dark:hover:bg-dark-800/50">
      <span className="font-medium text-dark-900 dark:text-dark-100">{region.region}</span>
      <div className="flex items-center gap-3 text-sm">
        <span className={cn(
          'px-2 py-0.5 rounded-full text-xs font-medium',
          region.status === 'healthy' && 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
          region.status === 'degraded' && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
        )}>
          {region.status}
        </span>
        <span className="text-dark-500 font-mono">{region.traffic}</span>
        {region.incidents > 0 && (
          <span className="px-2 py-0.5 text-xs bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 rounded">
            {region.incidents} incidents
          </span>
        )}
      </div>
    </div>
  )
}

export function DigitalHeartbeat() {
  return (
    <div className="flex flex-col h-full p-4 lg:p-6 overflow-y-auto space-y-6">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-dark-900 dark:text-dark-100 mb-2">
          Digital Heartbeat
        </h1>
        <p className="text-dark-600 dark:text-dark-400">
          The internet's vital signs — edits, code, trends, and connectivity
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Section title="Live Wikipedia Edits" icon={Activity} status="live">
          <div className="space-y-1">
            {wikiEdits.map((edit, i) => (
              <WikiEditRow key={i} edit={edit} />
            ))}
          </div>
        </Section>
        
        <Section title="GitHub Global Activity" icon={Github} status="active">
          <div className="space-y-1">
            {githubEvents.map((event, i) => (
              <GHEventRow key={i} event={event} />
            ))}
          </div>
        </Section>
        
        <Section title="Hacker News Trends" icon={Zap} status="trending">
          <div className="space-y-1">
            {hnStories.map((story, i) => (
              <HNStoryRow key={i} story={story} />
            ))}
          </div>
        </Section>
        
        <Section title="Cloudflare Radar — Internet Health" icon={Wifi} status="healthy">
          <div className="space-y-1">
            {cloudflareData.map((region, i) => (
              <CFRegionRow key={i} region={region} />
            ))}
          </div>
        </Section>
      </div>
    </div>
  )
}