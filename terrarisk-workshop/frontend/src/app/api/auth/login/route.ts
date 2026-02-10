import { NextResponse } from 'next/server';

const WORKSHOP_PASSWORD = process.env.WORKSHOP_ACCESS_PASSWORD || 'TerraRisk2026!SEMIL';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'TR-Admin-Adrian2026!';
const AUTH_COOKIE = 'tr-workshop-auth';
const ADMIN_COOKIE = 'tr-admin-auth';

function hashPassword(password: string): string {
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return `tr-${Math.abs(hash).toString(36)}`;
}

export async function POST(request: Request) {
  const { password, isAdmin } = await request.json();

  const expectedPassword = isAdmin ? ADMIN_PASSWORD : WORKSHOP_PASSWORD;
  const cookieName = isAdmin ? ADMIN_COOKIE : AUTH_COOKIE;

  if (password !== expectedPassword) {
    return NextResponse.json({ error: 'Incorrect password' }, { status: 401 });
  }

  const response = NextResponse.json({ success: true });

  // Set auth cookie - expires in 7 days
  response.cookies.set(cookieName, hashPassword(expectedPassword), {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  });

  // If admin login, also set workshop cookie
  if (isAdmin) {
    response.cookies.set(AUTH_COOKIE, hashPassword(WORKSHOP_PASSWORD), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
      path: '/',
    });
  }

  return response;
}
