#include "pch_script.h"

#include "physics_element_scripted.h"

using namespace luabind;

Fmatrix global_transform(cphysics_element_scripted* E)
{
	Fmatrix m;
	E->GetGlobalTransformDynamic(&m);
	return m;
}

void lewd_engine_feature_add(LPCSTR name); // script_ini_file_script.cpp

void cphysics_element_scripted::script_register(lua_State* L)
{
	lewd_engine_feature_add("mass_center"); // LEWD B6
	module(L)
	[
		class_<cphysics_element_scripted>("physics_element")
		.def("apply_force",
		     (void (cphysics_element_scripted::*)(float, float, float))(&cphysics_element_scripted::applyForce))

		// demonized: apply_torque
		.def("apply_torque",
			(void (cphysics_element_scripted::*)(float, float, float))(&cphysics_element_scripted::applyTorque))

		.def("is_breakable", &cphysics_element_scripted::isBreakable)
		.def("get_linear_vel", &cphysics_element_scripted::get_LinearVel)
		.def("get_angular_vel", &cphysics_element_scripted::get_AngularVel)
		.def("get_mass", &cphysics_element_scripted::getMass)
		.def("get_density", &cphysics_element_scripted::getDensity)
		.def("get_volume", &cphysics_element_scripted::getVolume)
		.def("fix", &cphysics_element_scripted::Fix)
		.def("release_fixed", &cphysics_element_scripted::ReleaseFixed)
		.def("is_fixed", &cphysics_element_scripted::isFixed)
		.def("global_transform", &global_transform)
		// LEWD B6
		.def("set_mass_center", &cphysics_element_scripted::set_mass_center)
		.def("get_mass_center", &cphysics_element_scripted::get_mass_center)
		.def("get_mass_center_world", &cphysics_element_scripted::get_mass_center_world)
		.def("set_mass", &cphysics_element_scripted::set_mass)
	];
}
