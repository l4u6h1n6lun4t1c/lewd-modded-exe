#pragma once
// LEWD AUTOTEST: unattended smoke-test mode, switched on by the -lewd_autotest command line flag.
// Without the flag every check below is false and the engine behaves exactly as before.
// Header-only on purpose: each module gets its own cached copy, no export needed.
#include <windows.h>
#include <string.h>

inline bool lewd_autotest()
{
	static const bool on = strstr(GetCommandLineA(), "-lewd_autotest") != nullptr;
	return on;
}

// Off-screen spot for the game window: just right of every monitor, so it renders but is never seen.
inline void lewd_autotest_window_pos(int& x, int& y)
{
	x = GetSystemMetrics(SM_XVIRTUALSCREEN) + GetSystemMetrics(SM_CXVIRTUALSCREEN) + 64;
	y = GetSystemMetrics(SM_YVIRTUALSCREEN);
}

// Wall clock in ms (QPC), shared by the audio start mark and the per-frame video times.
inline double lewd_autotest_wall_ms()
{
	LARGE_INTEGER f, c;
	QueryPerformanceFrequency(&f);
	QueryPerformanceCounter(&c);
	return double(c.QuadPart) * 1000.0 / double(f.QuadPart);
}

// The run's work folder = the folder of "-lewd_autotest_plan <file>". Empty when not in test mode.
inline void lewd_autotest_work_dir(char* out, size_t n)
{
	out[0] = 0;
	if (!lewd_autotest())
		return;
	const char* a = strstr(GetCommandLineA(), "-lewd_autotest_plan");
	if (!a)
		return;
	a += strlen("-lewd_autotest_plan");
	while (*a == ' ' || *a == '"')
		++a;
	size_t i = 0;
	while (a[i] && a[i] != ' ' && a[i] != '"' && i + 1 < n)
	{
		out[i] = a[i];
		++i;
	}
	out[i] = 0;
	char* slash = strrchr(out, '\\');
	char* slash2 = strrchr(out, '/');
	if (slash2 > slash)
		slash = slash2;
	if (slash)
		*slash = 0;
	else
		out[0] = 0;
}

// true once the sound system was pointed at the WAV writer (then the listener must NOT be muted)
inline bool lewd_autotest_audio_capture()
{
	char v[8];
	return GetEnvironmentVariableA("LEWD_AUTOTEST_AUDIO", v, sizeof(v)) > 0;
}

// Game-clock audio capture: samples written to game_audio.wav so far (-1 = not capturing). Lives in xrCore.
#ifdef XRCORE_API
XRCORE_API extern volatile __int64 g_lewd_audio_samples;
#endif
static const int lewd_autotest_audio_rate = 48000;
