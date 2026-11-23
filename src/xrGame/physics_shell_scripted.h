#pragma once

#include "../xrphysics/iphysics_scripted.h"
#include "../xrphysics/physicsshell.h"
#include "script_export_space.h"

class CPhysicsShell;
class cphysics_element_scripted;
class cphysics_joint_scripted;

class cphysics_shell_scripted :
	public cphysics_game_scripted<CPhysicsShell>
{
public:
	cphysics_shell_scripted(CPhysicsShell* imp): cphysics_game_scripted<CPhysicsShell>(imp)
	{
	}


	void applyForce(float x, float y, float z) { physics_impl().applyForce(x, y, z); }

	// island exact-integration opt-in (see CPHIsland::Step)
	void setForceExactIntegration() { physics_impl().SetForceExactIntegration(); }

	// demonized: applyTorque
	void applyTorque(float x, float y, float z) { physics_impl().applyTorque(x, y, z); }
	void applyRelTorque(float x, float y, float z) { physics_impl().applyRelTorque(x, y, z); }

	cphysics_element_scripted* get_Element(LPCSTR bone_name);
	cphysics_element_scripted* get_Element(u16 bone_id);
	cphysics_element_scripted* get_ElementByStoreOrder(u16 idx);

	u16 get_ElementsNumber() { return physics_impl().get_ElementsNumber(); }

	cphysics_joint_scripted* get_Joint(LPCSTR bone_name);
	cphysics_joint_scripted* get_Joint(u16 bone_id);
	cphysics_joint_scripted* get_JointByStoreOrder(u16 idx);

	//&cphysics_shell_scripted::get_JointByStoreOrder)

	u16 get_JointsNumber() { return physics_impl().get_JointsNumber(); }
	void BlockBreaking() { physics_impl().BlockBreaking(); }
	void UnblockBreaking() { physics_impl().UnblockBreaking(); }
	bool IsBreakingBlocked() { return physics_impl().IsBreakingBlocked(); }
	bool isBreakable() { return physics_impl().isBreakable(); }
	void get_LinearVel(Fvector& velocity) const { physics_impl().get_LinearVel(velocity); }
	void set_LinearVel(Fvector& velocity) { physics_impl().set_LinearVel(velocity); }
	void get_AngularVel(Fvector& velocity) const { physics_impl().get_AngularVel(velocity); }
	void set_AngularVel(Fvector& velocity) { physics_impl().set_AngularVel(velocity); }
    void set_DynamicLimits(float l, float w) { physics_impl().set_DynamicLimits(l, w); }
	void freeze();
	void unfreeze();
	void SetScale(Fvector scale);
    void SetScale(float scale) { SetScale(Fvector().set(scale, scale, scale)); }
	Fvector GetScale();
	float GetMass();

	// LEWD B1: collision filter class bits (CPHCollideValidator::ETypeFlags) from Lua.
	// The bits live on the shell's CPHObject, so they cover every element of the shell,
	// are read by every collision test (next physics step) and survive Deactivate/Activate
	// (only the CPHObject constructor resets them). Every setter is two-way.
	enum
	{
		lewd_cbNCStatic = 1 << 1,
		lewd_cbClassDynamic = 1 << 2,
		lewd_cbNCClassDynamic = 1 << 3,
		lewd_cbNCClassCharacter = 1 << 5,
		lewd_cbClassSmall = 1 << 6,
		lewd_cbNCClassSmall = 1 << 7,
		lewd_cbClassRagDoll = 1 << 8,
		lewd_cbNCClassRagDoll = 1 << 9,
		lewd_cbClassAnimated = 1 << 10,
		lewd_cbNCClassAnimated = 1 << 11,
	};
	void set_cl_bit(u32 bit, bool v) { physics_impl().collide_class_bits().set(bit, v ? TRUE : FALSE); }
	bool get_cl_bit(u32 bit) { return !!physics_impl().collide_class_bits().test(bit); }

	void set_ignore_static(bool v) { set_cl_bit(lewd_cbNCStatic, v); }
	bool get_ignore_static() { return get_cl_bit(lewd_cbNCStatic); }
	void set_dynamic_class(bool v) { set_cl_bit(lewd_cbClassDynamic, v); }
	bool is_dynamic_class() { return get_cl_bit(lewd_cbClassDynamic); }
	void set_ignore_dynamic(bool v) { set_cl_bit(lewd_cbNCClassDynamic, v); }
	bool get_ignore_dynamic() { return get_cl_bit(lewd_cbNCClassDynamic); }
	void set_ignore_character(bool v) { set_cl_bit(lewd_cbNCClassCharacter, v); }
	bool get_ignore_character() { return get_cl_bit(lewd_cbNCClassCharacter); }
	void set_small(bool v) { set_cl_bit(lewd_cbClassSmall, v); }
	bool is_small() { return get_cl_bit(lewd_cbClassSmall); }
	void set_ignore_small(bool v) { set_cl_bit(lewd_cbNCClassSmall, v); }
	bool get_ignore_small() { return get_cl_bit(lewd_cbNCClassSmall); }
	void set_ragdoll(bool v) { set_cl_bit(lewd_cbClassRagDoll, v); }
	bool is_ragdoll() { return get_cl_bit(lewd_cbClassRagDoll); }
	void set_ignore_ragdoll(bool v) { set_cl_bit(lewd_cbNCClassRagDoll, v); }
	bool get_ignore_ragdoll() { return get_cl_bit(lewd_cbNCClassRagDoll); }
	void set_animated_class(bool v) { set_cl_bit(lewd_cbClassAnimated, v); }
	bool is_animated_class() { return get_cl_bit(lewd_cbClassAnimated); }
	void set_ignore_animated(bool v) { set_cl_bit(lewd_cbNCClassAnimated, v); }
	bool get_ignore_animated() { return get_cl_bit(lewd_cbNCClassAnimated); }
	u32 get_collide_class_bits() { return physics_impl().collide_class_bits().get(); }

	// LEWD B6: centre of mass of the root element (bone space of the root bone) and shell mass
	// (get_mass is upstream's GetMass)
	bool set_mass_center(const Fvector& local_mc);
	Fvector get_mass_center();
	Fvector get_mass_center_world();
	void set_mass(float M);
	void set_collide_class_bits(u32 bits) { physics_impl().collide_class_bits().assign(bits); }
DECLARE_SCRIPT_REGISTER_FUNCTION
};
