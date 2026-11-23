#pragma once
#include "../xrphysics/iphysics_scripted.h"
#include "../xrphysics/physicsshell.h"
#include "script_export_space.h"

class CPhysicsElement;

class cphysics_element_scripted :
	public cphysics_game_scripted<CPhysicsElement>
{
public:
	cphysics_element_scripted(CPhysicsElement* imp): cphysics_game_scripted<CPhysicsElement>(imp)
	{
	}

	void applyForce(float x, float y, float z) { physics_impl().applyForce(x, y, z); }

	// demonized: apply_torque
	void applyTorque(float x, float y, float z) { physics_impl().applyTorque(x, y, z); }

	bool isBreakable() { return physics_impl().isBreakable(); }
	void get_LinearVel(Fvector& velocity) const { physics_impl().get_LinearVel(velocity); }
	void get_AngularVel(Fvector& velocity) const { physics_impl().get_AngularVel(velocity); }


	float getMass() { return physics_impl().getMass(); }
	float getDensity() { return physics_impl().getDensity(); }
	float getVolume() { return physics_impl().getVolume(); }

	void Fix() { physics_impl().Fix(); }
	void ReleaseFixed() { physics_impl().ReleaseFixed(); }
	bool isFixed() { return physics_impl().isFixed(); }
	void GetGlobalTransformDynamic(Fmatrix* m) const { physics_impl().GetGlobalTransformDynamic(m); }

	// LEWD B6: live centre of mass (bone space) and mass
	bool set_mass_center(const Fvector& local_mc) { return physics_impl().lewd_set_mass_center_live(local_mc); }
	Fvector get_mass_center() { return physics_impl().local_mass_Center(); }
	Fvector get_mass_center_world()
	{
		if (!physics_impl().isActive()) return Fvector().set(0.f, 0.f, 0.f);
		return physics_impl().mass_Center();
	}
	void set_mass(float M) { physics_impl().lewd_set_mass_live(M); }

DECLARE_SCRIPT_REGISTER_FUNCTION
};
