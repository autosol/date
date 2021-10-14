#pragma once

#include <string>

//Adapted from https://github.com/libarchive/libarchive/blob/master/examples/untar.c
class untar
{
private:
	static int copy_data(struct archive* ar, struct archive* aw);

public:
	static bool extract(const std::string& filename, const std::string& destinationFolder);
};