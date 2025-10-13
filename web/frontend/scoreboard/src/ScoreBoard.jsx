import { useEffect, useState } from 'react'
import { API_BASE, fetchTop, claimScore, postAnonymousScore } from './api'

export default function Scoreboard(){
  const [scores, setScores] = useState([])
  const [error, setError] = useState('')


  const [scoreId, setScoreId] = useState('')
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [msg, setMsg] = useState('')

  // local testing only
  const [testScore, setTestScore] = useState('')

  // Initial load
  useEffect(()=>{
    fetchTop(10).then(setScores).catch(e=>setError(e.message))
  },[])


  useEffect(()=>{
    let pollId
    let ws
    try{
      ws = new WebSocket(API_BASE.replace(/^http/, 'ws') + '/ws')
      ws.onmessage = ()=> fetchTop(10).then(setScores).catch(console.error)
      ws.onerror = ()=>{  }
      ws.onclose = ()=>{ }
    }catch{ /* ignore */ }

    pollId = setInterval(()=>{
      fetchTop(10).then(setScores).catch(()=>{})
    }, 3000)

    return ()=>{ if (ws) ws.close(); clearInterval(pollId) }
  },[])

  async function onClaim(e){
    e.preventDefault()
    setMsg('')
    try{
      await claimScore(Number(scoreId), code.trim(), name.trim())
      setMsg('Claimed!')
      setScoreId(''); setCode(''); setName('')
      setScores(await fetchTop(10))
    }catch(err){ setMsg(String(err)) }
  }

  async function onTestPost(){
    setMsg('')
    try{
      const s = Number(testScore)
      if (!Number.isFinite(s) || s < 0) { setMsg('Enter a non-negative number'); return }
      const resp = await postAnonymousScore(s)
      const short = resp.claim_token.slice(-6)
      setMsg(`Posted id=${resp.id} code=${short}`)
      setScores(await fetchTop(10))
    }catch(err){ setMsg(String(err)) }
  }

  return (
    <div style={{width:'100%',maxWidth:720,background:'#fff',borderRadius:16,boxShadow:'0 10px 30px rgba(0,0,0,0.08)',padding:24}}>
      <h1 style={{margin:'0 0 12px',fontSize:24}}>🏆 Top Scorers</h1>

      {error && <div style={{color:'#b00020',marginBottom:12}}>{error}</div>}

      <table style={{width:'100%',borderCollapse:'collapse'}}>
        <thead>
          <tr style={{textAlign:'left',borderBottom:'1px solid #eee'}}>
            <th style={{padding:'8px 4px'}}>#</th>
            <th style={{padding:'8px 4px'}}>Player</th>
            <th style={{padding:'8px 4px'}}>Score</th>
          </tr>
        </thead>
        <tbody>
          {scores.map((s, i)=> (
            <tr key={s.id} style={{borderBottom:'1px solid #f2f2f2'}}>
              <td style={{padding:'8px 4px'}}>{i+1}</td>
              <td style={{padding:'8px 4px',fontWeight:600}}>{s.player || '— unclaimed —'}</td>
              <td style={{padding:'8px 4px'}}>{s.score}</td>
            </tr>
          ))}
          {scores.length === 0 && (
            <tr><td colSpan={3} style={{padding:12,color:'#666'}}>No scores yet</td></tr>
          )}
        </tbody>
      </table>

      <div style={{marginTop:24,display:'grid',gap:12}}>
        <form onSubmit={onClaim} style={{display:'grid',gap:8}}>
          <h2 style={{margin:0,fontSize:18}}>Claim Your Score</h2>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8}}>
            <input value={scoreId} onChange={e=>setScoreId(e.target.value)} placeholder="Score ID" />
            <input value={code} onChange={e=>setCode(e.target.value)} placeholder="Code (last 6 or full)" />
            <input value={name} onChange={e=>setName(e.target.value)} placeholder="Your name" />
          </div>
          <button type="submit" style={{justifySelf:'start',padding:'8px 12px'}}>Claim</button>
        </form>

        <div style={{borderTop:'1px solid #eee',paddingTop:12}}>
          <h3 style={{margin:'0 0 8px',fontSize:16}}>Local test (post anonymous score)</h3>
          <div style={{display:'grid',gridTemplateColumns:'1fr auto',gap:8}}>
            <input value={testScore} onChange={e=>setTestScore(e.target.value)} placeholder="Score (e.g., 250)" />
            <button type="button" onClick={onTestPost}>Post</button>
          </div>
        </div>

        {msg && <div style={{color:'#0a7',fontSize:14}}>{msg}</div>}
      </div>
    </div>
  )
}