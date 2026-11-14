import { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { Stars, OrbitControls } from '@react-three/drei'
import  './geo'
import { Line } from '@react-three/drei'
import { coastlineRings, landTexture } from './geo'
import { CameraLight } from './CameraLight'

import './App.css'

function App() {
  
  const [query, setQuery] = useState("")

  async function handleSubmit(e: React.SubmitEvent) {
  e.preventDefault()

  const res = await fetch(`/api/flight/${query}`)
  const data = await res.json()

  console.log(res.status, data)
}

  return (
    <main className="relative h-dvh">
      <title>Fly With Me</title>

      <header className='absolute top-4 left-4 z-10'>
        <h1 className='text-6xl text-black'>Fly With Me</h1>
      </header>

      <Canvas camera={{position : [0,0,2.5]}}>
        <color attach="background" args={['#eef0f2']} />
        <Stars radius={50} depth={50} count={300} factor={3} saturation={0} fade />
        <OrbitControls autoRotate autoRotateSpeed={1} enablePan={false} minDistance={1.5} maxDistance={5} />
        

        <ambientLight intensity={0.8} />
        <CameraLight />
        <mesh>
          <sphereGeometry args={[1, 64, 64]} />
          <meshBasicMaterial map={landTexture} />
        </mesh>

        {coastlineRings.map((ring, i) => (
          <Line key={i} points={ring} color="b9c2ca" lineWidth={1.0} />
        ))}

      </Canvas>


      <form className="absolute bottom-8 left-1/2 flex w-[90%] max-w-lg -translate-x-1/2 items-center gap-2 rounded-full border border-gray-300 bg-white py-2 pl-5 pr-2 shadow-sm"
      onSubmit={handleSubmit}>
        <input
          className="flex-1 bg-transparent text-lg text-black outline-none placeholder:text-gray-400"
          placeholder="Enter a flight number"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <button className="flex h-10 w-10 items-center justify-center rounded-full bg-black text-white">
          ↑
        </button>
    </form>
      
    </main>
  )
}
export default App
