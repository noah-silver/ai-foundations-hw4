export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_url: string
  price: number
  total_stock: number
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail extends Product {
  inventory: SizeStock[]
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export const fetchProducts = () => getJson<Product[]>('/api/products')

export const fetchProduct = (id: string) =>
  getJson<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

export const formatPrice = (price: number) =>
  price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })

// garment_type has ~22 inconsistent spellings in the catalogue, so group them for filtering.
export function category(garmentType: string): string {
  const g = garmentType.toLowerCase()
  if (g.includes('quarter-zip')) return 'Quarter-Zips'
  if (g.includes('jacket') || g.includes('full-zip')) return 'Jackets & Full-Zips'
  if (g.includes('hood')) return 'Hoodies'
  if (g.includes('crewneck') || g.includes('mockneck')) return 'Crewnecks'
  if (g.includes('t-shirt') || g.includes('shirt')) return 'Tees & Shirts'
  return 'Other'
}

export const CATEGORIES = ['Hoodies', 'Crewnecks', 'Quarter-Zips', 'Jackets & Full-Zips', 'Tees & Shirts']
