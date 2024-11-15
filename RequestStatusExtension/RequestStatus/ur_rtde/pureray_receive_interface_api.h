#pragma once
#ifndef PURERAY_RECEIVE_INTERFACE_API_H
#define PURERAY_RECEIVE_INTERFACE_API_H

#include <ur_rtde/rtde_export.h>
#include <ur_rtde/robot_state.h>
#include <ur_rtde/rtde_utility.h>

#include <atomic>
#include <chrono>
#include <memory>
#include <string>
#include <vector>
#include <map>
#include <functional>

#define MAJOR_VERSION 0
#define MINOR_VERSION 1
#define BUGFIX_VERSION 2
#define BUILD_VERSION 3
#define CB3_MAJOR_VERSION 3
#define RT_PRIORITY_UNDEFINED 0

// forward declarations
namespace boost
{
class thread;
}
namespace ur_rtde
{
class DashboardClient;
}
namespace ur_rtde
{
class RobotState;
}
namespace ur_rtde
{
class RTDE;
}

namespace ur_rtde
{
class PurerayReceiveInterfaceAPI
{
 public:
  /**
   * @returns Actual joint positions
   */
  RTDE_EXPORT virtual std::vector<double> getActualQ() = 0;

  /**
   * @returns Actual Cartesian coordinates of the tool: (x,y,z,rx,ry,rz), where rx, ry and rz is a rotation vector
   * representation of the tool orientation
   */
  RTDE_EXPORT virtual std::vector<double> getActualTCPPose() = 0;

};

}  // namespace ur_rtde

#endif  // PURERAY_RECEIVE_INTERFACE_API_H
