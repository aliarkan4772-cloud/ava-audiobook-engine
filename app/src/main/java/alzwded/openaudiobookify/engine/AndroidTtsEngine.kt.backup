package alzwded.openaudiobookify.engine

import android.os.Bundle
import android.speech.tts.TextToSpeech
import java.io.File

class AndroidTtsEngine(
    private val tts: TextToSpeech
) : SpeechEngine {

    override fun synthesize(
        text: String,
        outputFile: File,
        utteranceId: String
    ): Int {
        val params = Bundle().apply {
            putString(
                TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID,
                utteranceId
            )
        }

        return tts.synthesizeToFile(
            text,
            params,
            outputFile,
            utteranceId
        )
    }

    override fun stop() {
        tts.stop()
    }

    override fun shutdown() {
        tts.shutdown()
    }
}
