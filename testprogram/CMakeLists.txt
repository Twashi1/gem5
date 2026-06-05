cmake_minimum_required(VERSION 3.16)
project(gem5_marker C)

set(CMAKE_C_STANDARD 11)

add_executable(marker
    main.c
)

# Ensure no unwanted optimization removes marker
target_compile_options(marker PRIVATE -O0 -fno-inline)

target_link_options(marker PRIVATE
    -static
)
