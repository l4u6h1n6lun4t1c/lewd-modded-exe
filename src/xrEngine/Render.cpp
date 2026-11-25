#include "stdafx.h"
#include "render.h"

IRender_interface::~IRender_interface()
{
};

//ENGINE_API IRender_interface* Render = NULL;

// LEWD B12 camera occlusion fade (Render.h)
ENGINE_API SLewdCamOcclusion g_lewd_cam_occlusion;

ENGINE_API bool lewd_cam_occlusion_hit(const Fvector& center, float r)
{
	const SLewdCamOcclusion& o = g_lewd_cam_occlusion;
	const Fvector& a = Device.vCameraPosition;
	Fvector d;
	d.sub(o.target, a);
	const float len = d.magnitude();
	if (len < EPS_L)
		return false;
	d.div(len);
	const float seg = len - o.target_clear; // stop short of the target
	if (seg <= 0.f)
		return false;
	Fvector ac;
	ac.sub(center, a);
	float t = ac.dotproduct(d);
	if (t < 0.f) t = 0.f;
	else if (t > seg) t = seg;
	Fvector p;
	p.mad(a, d, t);
	const float rr = r + o.radius;
	return p.distance_to_sqr(center) < rr * rr;
}

ENGINE_API bool lewd_cam_occlusion_hit_box(const Fbox& box, const Fmatrix* xform)
{
	const SLewdCamOcclusion& o = g_lewd_cam_occlusion;
	Fvector a = Device.vCameraPosition;
	Fvector d;
	d.sub(o.target, a);
	const float len = d.magnitude();
	if (len < EPS_L)
		return false;
	const float seg = len - o.target_clear;
	if (seg <= 0.f)
		return false;
	d.mul(seg / len);
	Fvector b;
	b.add(a, d);
	if (xform)
	{
		Fmatrix inv;
		inv.invert(*xform);
		inv.transform_tiny(a);
		inv.transform_tiny(b);
	}
	Fbox bb = box;
	bb.grow(o.radius);
	// slab test of the segment a..b against bb
	float t0 = 0.f, t1 = 1.f;
	const float pa[3] = {a.x, a.y, a.z};
	const float pd[3] = {b.x - a.x, b.y - a.y, b.z - a.z};
	const float mn[3] = {bb.min.x, bb.min.y, bb.min.z};
	const float mx[3] = {bb.max.x, bb.max.y, bb.max.z};
	for (int i = 0; i < 3; ++i)
	{
		if (_abs(pd[i]) < EPS_S)
		{
			if (pa[i] < mn[i] || pa[i] > mx[i])
				return false;
			continue;
		}
		float ta = (mn[i] - pa[i]) / pd[i];
		float tb = (mx[i] - pa[i]) / pd[i];
		if (ta > tb) std::swap(ta, tb);
		if (ta > t0) t0 = ta;
		if (tb < t1) t1 = tb;
		if (t0 > t1)
			return false;
	}
	return true;
}

// resources
IRender_Light::~IRender_Light()
{
	::Render->light_destroy(this);
}

IRender_Glow::~IRender_Glow()
{
	::Render->glow_destroy(this);
}
