
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $Width = $Screen.Width
        $Height = $Screen.Height
        $Left = $Screen.Left
        $Top = $Screen.Top
        
        # Send debug info to stderr
        [Console]::Error.WriteLine("PowerShell Screenshot: Capturing $Width x $Height screen at ($Left, $Top)")
        
        try {
            # Create bitmap and grab screen
            $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size)
            
            # Convert to base64 string
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            [Console]::Error.WriteLine("PowerShell Screenshot: Successfully captured $($bytes.Length) bytes")
            
            # Output the base64 string to stdout (this is the only stdout output)
            Write-Output $base64
            $bitmap.Dispose()
            $ms.Dispose()
        }
        catch {
            [Console]::Error.WriteLine("PowerShell Screenshot Error: Failed to capture screenshot: $_")
            Write-Error "Failed to capture screenshot: $_"
            exit 1
        }
        