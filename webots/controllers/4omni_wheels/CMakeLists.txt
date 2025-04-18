cmake_minimum_required(VERSION 3.5)

# Setup the project.
get_filename_component(PROJECT ${CMAKE_SOURCE_DIR} NAME)
project(${PROJECT})

# Get C or C++ sources in the current directory.
file(GLOB C_SOURCES *.c)
file(GLOB CPP_SOURCES *.cpp)
set(SOURCES ${C_SOURCES} ${CPP_SOURCES})

# Set the Webots home path
set(WEBOTS_HOME "/usr/local/webots")

# Link with the Webots controller library
link_directories(${WEBOTS_HOME}/lib/webots)
include_directories(${WEBOTS_HOME}/include/controller/c ${WEBOTS_HOME}/include/controller/cpp)

# Setup OpenCV if needed
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

# Set libraries to link
set(LIBRARIES m ${CMAKE_SHARED_LIBRARY_PREFIX}Controller${CMAKE_SHARED_LIBRARY_SUFFIX} ${CMAKE_SHARED_LIBRARY_PREFIX}CppController${CMAKE_SHARED_LIBRARY_SUFFIX})

link_directories(/usr/local/webots/lib/controller)

# Setup the target executable
add_executable(${PROJECT} ${SOURCES})
target_link_libraries(${PROJECT} 
    ${LIBRARIES} 
    ${OpenCV_LIBRARIES} 
    Controller
    CppController
)

# Copy the target executable to the correct location
add_custom_command(TARGET ${PROJECT} POST_BUILD COMMAND ${CMAKE_COMMAND} -E
  copy ${CMAKE_BINARY_DIR}/${PROJECT} ${CMAKE_SOURCE_DIR}
)
