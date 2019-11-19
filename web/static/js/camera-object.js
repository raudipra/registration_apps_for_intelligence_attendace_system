class CameraObject {
    constructor(deviceId, videoNodeId, canvasNodeId, width = 720, height = null) {
        /**
         * Represents the media deviceId
         * @type {string}
         */
        this.deviceId = deviceId
        /**
         * Represents the video node
         * @type {Node}
         */
        this.video = document.getElementById(videoNodeId)
        /**
         * Represents the canvas node
         * @type {Node}
         */
        this.canvas = document.getElementById(canvasNodeId)
        /**
         * Width of the video stream
         * @type {number}
         */
        this.width = width
        /**
         * Height of the video stream
         * @type {number}
         */
        this.height = height
        /**
         * Indicates whether the stream is playing/not
         * @type {boolean}
         */
        this.streaming = false
        /**
         * Represents the stream
         * @type {MediaStream|null}
         */
        this.stream = null

        // apply stream handling to the video node
        this.video.addEventListener('canplay', function () {
            const video = this.video
            this.height = video.videoHeight / (video.videoWidth / this.width)
            video.setAttribute('width', this.width)
            video.setAttribute('height', this.height)

            this.streaming = true
        }.bind(this))
    }

    /**
      * Get predefined media constraints
      * @return {Object}
      **/
    get mediaConstraints() {
        return { video: { deviceId: this.deviceId ? { exact: this.deviceId } : undefined } }
    }

    /**
      * Get the parent element of the video node
      * @return {Node}
      **/
    get videoParent() {
        return this.video.parentNode
    }

    /**
      * Get the parent element of the canvas node
      * @return {Node}
      **/
    get canvasParent() {
        return this.canvas.parentNode
    }

    /**
      * Get current content of canvas as PNG
      * @return {string}
      **/
    get canvasContentPNG() {
        return this.canvas.toDataURL('image/png')
    }

    /**
     * Get canvas content as Blob
     * @return {Promise<Blob>}
     */
    get canvasContentBlobPromise() {
        const canvas = this.canvas
        return new Promise((resolve, reject) => {
            try {
                canvas.toBlob(blob => {
                    resolve(blob)
                })
            } catch (err) {
                reject(err)
            }
        })
    }

    /**
     * Shows/hides the canvas
     * @param {boolean} isVisible
     */
    setCanvasVisible(isVisible) {
        if (isVisible) {
            $(this.canvas.parentNode).removeClass('d-none')
        } else {
            $(this.canvas.parentNode).addClass('d-none')
        }
    }

    /**
     * Shows/hides the video
     * @param {boolean} isVisible
     */
    setVideoVisible(isVisible) {
        if (isVisible) {
            $(this.video.parentNode).removeClass('d-none')
        } else {
            $(this.video.parentNode).addClass('d-none')
        }
    }

    /**
     * Clears content of the current canvas
     */
    clearCanvas() {
        const context = this.canvas.getContext('2d')
        context.fillStyle = '#FFF'
        context.fillRect(0, 0, this.canvas.width, this.canvas.height)
    }

    /**
     * Takes snapshot from stream to canvas
     */
    captureSnapshotFromCurrentStream() {
        if (!this.stream) {
            return
        }

        const canvas = this.canvas
        const context = canvas.getContext('2d')
        if (this.width && this.height) {
            canvas.width = this.width
            canvas.height = this.height
            context.drawImage(this.video, 0, 0, this.width, this.height)
        }
    }

    /**
     * Attach a new stream
     * @param {MediaStream} stream the new stream to attach to
     */
    attachStream(stream) {
        this.stream = stream
        this.video.srcObject = stream
        this.video.play()
    }

    /**
     * Resume the current stream
     **/
    resumeStream() {
        if (!this.stream) return

        this.streaming = true
        this.video.play()
    }

    /**
     * Pauses the current stream
     **/
    pauseStream() {
        if (!this.stream) return

        this.streaming = false
        this.video.pause()
    }
}
