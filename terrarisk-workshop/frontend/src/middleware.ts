import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const WORKSHOP_PASSWORD = process.env.WORKSHOP_ACCESS_PASSWORD || 'TerraRisk2026!SEMIL';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'TR-Admin-Adrian2026!';
const AUTH_COOKIE = 'tr-workshop-auth';
const ADMIN_COOKIE = 'tr-admin-auth';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow access to the login page and all API routes (backend handles its own auth)
  if (pathname === '/login' || pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // Allow static assets and favicon
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/favicon') ||
    pathname.endsWith('.ico') ||
    pathname.endsWith('.png') ||
    pathname.endsWith('.jpg') ||
    pathname.endsWith('.svg')
  ) {
    return NextResponse.next();
  }

  // Check admin routes - require admin auth
  if (pathname.startsWith('/admin')) {
    const adminAuth = request.cookies.get(ADMIN_COOKIE)?.value;
    if (adminAuth !== hashPassword(ADMIN_PASSWORD)) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('admin', 'true');
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }
    return NextResponse.next();
  }

  // Check workshop auth for all other routes
  const workshopAuth = request.cookies.get(AUTH_COOKIE)?.value;
  if (workshopAuth !== hashPassword(WORKSHOP_PASSWORD)) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

// Simple hash for cookie value (not crypto-secure, just prevents plain text)
function hashPassword(password: string): string {
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return `tr-${Math.abs(hash).toString(36)}`;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
