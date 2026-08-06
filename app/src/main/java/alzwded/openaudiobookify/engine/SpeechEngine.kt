package alzwded.openaudiobookify.engine

import java.io.File

interface SpeechEngine {
    fun synthesize(
        text: String,
        outputFile: File,
        utteranceId: String
    ): Int

    fun stop()
    fun shutdown()
}
