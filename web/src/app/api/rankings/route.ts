import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const season = searchParams.get('season') || '2025'
    const qualified = searchParams.get('qualified') || 'false'
    const limit = searchParams.get('limit') || '570'
    const offset = searchParams.get('offset') || '0'
    
    // Make the API call from the server side
    const baseApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const apiUrl = `${baseApiUrl}/api/seasons/${season}/rankings?qualified=${qualified}&limit=${limit}&offset=${offset}`
    
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      cache: 'no-cache'
    })
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Return the data with proper CORS headers
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    })
  } catch (error) {
    console.error('Proxy API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch data from backend API' },
      { status: 500 }
    )
  }
}