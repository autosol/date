#include "date/untar.h"
#include "archive_entry.h"
#include "archive.h"
#include <string>
#include <cassert>

#ifdef _WIN32
typedef SSIZE_T ssize_t;
#else
#include "sys/types.h"
#endif

int untar::copy_data(struct archive* ar, struct archive* aw)
{
	int r;
	const void* buff;
	size_t size;
#if ARCHIVE_VERSION_NUMBER >= 3000000
	int64_t offset;
#else
	off_t offset;
#endif

	for (;;) {
		r = archive_read_data_block(ar, &buff, &size, &offset);
		if (r == ARCHIVE_EOF)
			return (ARCHIVE_OK);
		if (r != ARCHIVE_OK)
			return (r);
		r = archive_write_data_block(aw, buff, size, offset);
		if (r != ARCHIVE_OK) {
			assert(false);
			return (r);
		}
	}
}

bool untar::extract(const std::string& filename, const std::string& destinationFolder)
{
	struct archive* output = archive_write_disk_new();
	int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM | ARCHIVE_EXTRACT_ACL | ARCHIVE_EXTRACT_FFLAGS;
	archive_write_disk_set_options(output, flags);

	struct archive* input = archive_read_new();
	archive_read_support_format_tar(input);
	archive_read_support_compression_gzip(input);

	int result;
	if ((result = archive_read_open_filename(input, filename.c_str(), 10240)))
	{
		assert(false);
		return false;
	}

	struct archive_entry* entry;
	for (;;)
	{
		result = archive_read_next_header(input, &entry);
		if (result == ARCHIVE_EOF)
			break;
		if (result != ARCHIVE_OK)
		{
			assert(false);
			return false;
		}

		std::string currentFile = archive_entry_pathname(entry);
		const std::string fullOutputPath = destinationFolder + "\\" + currentFile;
		archive_entry_set_pathname(entry, fullOutputPath.c_str());

		result = archive_write_header(output, entry);
		if (result != ARCHIVE_OK)
			assert(false);
		else
		{
			copy_data(input, output);
			result = archive_write_finish_entry(output);
			if (result != ARCHIVE_OK)
			{
				assert(false);
				return false;
			}
		}
	}

	archive_read_close(input);
	archive_read_free(input);

	archive_write_close(output);
	archive_write_free(output);
	return true;
}
