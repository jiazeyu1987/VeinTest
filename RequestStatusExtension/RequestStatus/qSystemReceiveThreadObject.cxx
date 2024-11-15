#include "qSystemReceiveThreadObject.h"

qSystemReceiveThreadObject::qSystemReceiveThreadObject() {
	JQCPUMonitor::initialize();
}

void qSystemReceiveThreadObject::findCPUUsage(const char* processName) {
	HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	if (hProcessSnap == INVALID_HANDLE_VALUE) return;

	PROCESSENTRY32 pe32;
	pe32.dwSize = sizeof(PROCESSENTRY32);

	if (Process32First(hProcessSnap, &pe32)) {
		do {
			if (strcmp(pe32.szExeFile, processName) == 0) {
				HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pe32.th32ProcessID);
				if (hProcess != NULL) {
					FILETIME ftSysIdle, ftSysKernel, ftSysUser;
					FILETIME ftProcCreation, ftProcExit, ftProcKernel, ftProcUser;
					ULONGLONG sysKernelBefore, sysUserBefore, procKernelBefore, procUserBefore;
					ULONGLONG sysKernelAfter, sysUserAfter, procKernelAfter, procUserAfter;

					// ��ȡϵͳ�ͽ��̵�CPUʱ�䣨ǰ��
					GetSystemTimes(&ftSysIdle, &ftSysKernel, &ftSysUser);
					GetProcessTimes(hProcess, &ftProcCreation, &ftProcExit, &ftProcKernel, &ftProcUser);
					sysKernelBefore = ((ULARGE_INTEGER*)&ftSysKernel)->QuadPart;
					sysUserBefore = ((ULARGE_INTEGER*)&ftSysUser)->QuadPart;
					procKernelBefore = ((ULARGE_INTEGER*)&ftProcKernel)->QuadPart;
					procUserBefore = ((ULARGE_INTEGER*)&ftProcUser)->QuadPart;

					std::string value = QString::number(sysKernelBefore).toStdString();
					std::string value1 = QString::number(sysUserBefore).toStdString();
					std::string value2 = QString::number(procKernelBefore).toStdString();
					std::string value3 = QString::number(procUserBefore).toStdString();
					map_info["cpu"] = value;
					map_info["cpu1"] = value1;
					map_info["cpu2"] = value2;
					map_info["cpu3"] = value3;
					CloseHandle(hProcess);
				}
			}
		} while (Process32Next(hProcessSnap, &pe32));
	}
	CloseHandle(hProcessSnap);
}

void qSystemReceiveThreadObject::OnReceiveObjectInnerTick() {
	findProcessUsage("SlicerApp-real.exe");
	map_info["cpu"] = JQCPUMonitor::cpuUsagePercentageDisplayString().toStdString();
}

qSystemReceiveThreadObject::~qSystemReceiveThreadObject() {}

void qSystemReceiveThreadObject::findProcessUsage(const char* processName) {
	HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	if (hProcessSnap == INVALID_HANDLE_VALUE) return;

	PROCESSENTRY32 pe32;
	pe32.dwSize = sizeof(PROCESSENTRY32);

	if (Process32First(hProcessSnap, &pe32)) {
		do {
			if (strcmp(pe32.szExeFile, processName) == 0) {
				HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pe32.th32ProcessID);
				if (hProcess != NULL) {
					PROCESS_MEMORY_COUNTERS pmc;
					if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
						// ����ڴ�ʹ�����
						//std::cout << "Memory Usage: " << int(pmc.WorkingSetSize/1024/1024) << " M\n";
						map_info["memory"] = QString::number(int(pmc.WorkingSetSize / 1024 / 1024)).toStdString();
						CloseHandle(hProcessSnap);
						return;
					}
					CloseHandle(hProcess);
				}
			}
		} while (Process32Next(hProcessSnap, &pe32));
	}
	CloseHandle(hProcessSnap);
}