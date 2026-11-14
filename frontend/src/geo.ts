import land from 'world-atlas/land-110m.json'
import { feature } from 'topojson-client'
import { Vector3, CanvasTexture, SRGBColorSpace } from 'three'

export const landGeo = feature(land as any, (land as any).objects.land)
const polygons = (landGeo as any).features[0].geometry.coordinates

export function latLonToVec(lat: number, lon: number, radius = 1): Vector3 {
  const la = lat * (Math.PI / 180)
  const lo = lon * (Math.PI / 180)
  return new Vector3(
    radius * Math.cos(la) * Math.cos(lo),
    radius * Math.sin(la),
    -radius * Math.cos(la) * Math.sin(lo),
  )
}

export const coastlineRings: Vector3[][] = []

for (const polygon of polygons) {
  for (const ring of polygon) {
    const points: Vector3[] = []
    for (const [lon, lat] of ring) {
      points.push(latLonToVec(lat, lon, 1.001))
    }
    coastlineRings.push(points)
  }
}

const WATER = '#cdd8e1'
const LAND = '#f8f8f6'

// Turn a ring's [lon, lat] points into continuous longitudes (no jumps at the
// 180° line), then shift the whole ring so it sits around -180..180.
function unwrapRing(ring: number[][]): number[][] {
  const out: number[][] = []
  let prevLon: number | null = null
  let offset = 0
  for (const [lon, lat] of ring) {
    if (prevLon !== null) {
      const jump = lon - prevLon
      if (jump > 180) offset -= 360
      else if (jump < -180) offset += 360
    }
    prevLon = lon
    out.push([lon + offset, lat])
  }

  const lons = out.map(([lon]) => lon)
  const middle = (Math.min(...lons) + Math.max(...lons)) / 2
  const recentre = -360 * Math.round(middle / 360)
  return out.map(([lon, lat]) => [lon + recentre, lat])
}

function makeLandTexture(): CanvasTexture {
  const W = 4096
  const H = 2048
  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')!

  ctx.fillStyle = WATER
  ctx.fillRect(0, 0, W, H)

  ctx.fillStyle = LAND
  for (const polygon of polygons) {
    const rings = polygon.map(unwrapRing)

    for (const shift of [-W, 0, W]) {
      ctx.beginPath()
      for (const ring of rings) {
        const toX = (lon: number) => ((lon + 180) / 360) * W + shift
        const toY = (lat: number) => ((90 - lat) / 180) * H

        ring.forEach(([lon, lat], i) => {
          if (i === 0) ctx.moveTo(toX(lon), toY(lat))
          else ctx.lineTo(toX(lon), toY(lat))
        })

        // A ring that circles the pole (Antarctica) ends a full lap from its
        // start: close it along the bottom edge instead of straight across.
        const firstLon = ring[0][0]
        const lastLon = ring[ring.length - 1][0]
        if (Math.abs(lastLon - firstLon) > 180) {
          ctx.lineTo(toX(lastLon), H)
          ctx.lineTo(toX(firstLon), H)
        }

        ctx.closePath()
      }
      ctx.fill('evenodd')
    }
  }

  const texture = new CanvasTexture(canvas)
  texture.colorSpace = SRGBColorSpace
  texture.anisotropy = 16
  return texture
}

export const landTexture = makeLandTexture()