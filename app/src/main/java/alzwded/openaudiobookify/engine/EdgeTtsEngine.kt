package alzwded.openaudiobookify.engine

import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.json.JSONObject
import java.io.File
import java.io.IOException

class EdgeTtsEngine(
    private val serverUrl: String,
    private val voice: String = "fa-IR-DilaraNeural"
) {
    private val client = OkHttpClient()

    fun synthesize(
        text: String,
        outputFile: File,
        onSuccess: (File) -> Unit,
        onError: (String) -> Unit
    ) {
        val json = JSONObject().apply {
            put("text", text)
            put("voice", voice)
        }

        val request = Request.Builder()
            .url("$serverUrl/tts")
            .post(
                json.toString()
                    .toRequestBody("application/json".toMediaType())
            )
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                onError(e.message ?: "Network error")
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) {
                        onError("HTTP ${response.code}")
                        return
                    }

                    val body = response.body ?: run {
                        onError("Empty response")
                        return
                    }

                    outputFile.outputStream().use { output ->
                        body.byteStream().copyTo(output)
                    }

                    onSuccess(outputFile)
                }
            }
        })
    }
}
