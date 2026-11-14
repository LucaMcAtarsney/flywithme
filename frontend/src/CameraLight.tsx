import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { DirectionalLight } from 'three'

export function CameraLight() {
  const light = useRef<DirectionalLight>(null)

  useFrame(({ camera }) => {
    light.current?.position.copy(camera.position)
  })

  return <directionalLight ref={light} intensity={1.5} />
}