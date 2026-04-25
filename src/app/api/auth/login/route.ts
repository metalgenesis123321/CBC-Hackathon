import { NextRequest, NextResponse } from "next/server";
import { findUserByEmail, verifyPassword, createToken, setAuthCookie, hashPassword, createUserWithEmail } from "@/lib/auth";

export async function POST(req: NextRequest) {
  try {
    const { email, password } = await req.json();

    if (!email || !password) {
      return NextResponse.json({ error: "Email and password required" }, { status: 400 });
    }

    const user = await findUserByEmail(email);

    if (!user || !user.password_hash) {
      if (password.length < 6) {
        return NextResponse.json({ error: "Password must be at least 6 characters" }, { status: 400 });
      }
      const defaultName = email.split("@")[0];
      const passwordHash = await hashPassword(password);
      const newUser = await createUserWithEmail(email, passwordHash, defaultName);
      const token = await createToken(newUser.id);
      const response = NextResponse.json({
        user: { id: newUser.id, email: newUser.email, name: newUser.name, onboarded: false },
        created: true,
      });
      return setAuthCookie(response, token);
    }

    const valid = await verifyPassword(password, user.password_hash);
    if (!valid) {
      return NextResponse.json({ error: "Invalid email or password" }, { status: 401 });
    }

    const token = await createToken(user.id);
    const response = NextResponse.json({
      user: {
        id: user.id, email: user.email, name: user.name,
        avatar_url: user.avatar_url, onboarded: user.onboarded,
      },
    });
    return setAuthCookie(response, token);
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json({ error: "Login failed" }, { status: 500 });
  }
}
